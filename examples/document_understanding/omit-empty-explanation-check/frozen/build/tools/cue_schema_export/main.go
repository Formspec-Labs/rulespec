// Export validation through native CUE and report source metadata separately.
// This adapter does not translate CUE expressions into validation constraints.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"runtime/debug"
	"strings"

	"cuelang.org/go/cue"
	"cuelang.org/go/cue/cuecontext"
	"cuelang.org/go/cue/literal"
	"cuelang.org/go/cue/load"
	"cuelang.org/go/encoding/jsonschema"
)

type metadata struct {
	Title      string               `json:"title,omitempty"`
	SortEnum   bool                 `json:"sortEnum,omitempty"`
	Order      []string             `json:"order,omitempty"`
	Properties map[string]*metadata `json:"properties,omitempty"`
	Items      *metadata            `json:"items,omitempty"`
}

func describe(value cue.Value, depth int) (*metadata, error) {
	if depth > 32 {
		return nil, fmt.Errorf("schema metadata exceeds the supported nesting depth")
	}
	result := &metadata{}
	attrs := value.Attributes(cue.ValueAttr)
	if len(attrs) == 0 {
		attrs = cue.Dereference(value).Attributes(cue.ValueAttr)
	}
	for _, attr := range attrs {
		if attr.Name() == "sortEnum" {
			if strings.TrimSpace(attr.Contents()) != "" {
				return nil, fmt.Errorf("%s: @sortEnum takes no arguments", value.Path())
			}
			result.SortEnum = true
		}
		if attr.Name() != "title" {
			continue
		}
		if attr.NumArgs() != 1 {
			return nil, fmt.Errorf("%s: @title requires one string", value.Path())
		}
		title, err := literal.Unquote(strings.TrimSpace(attr.RawArg(0)))
		if err != nil {
			return nil, fmt.Errorf("%s: invalid @title: %w", value.Path(), err)
		}
		if result.Title != "" && result.Title != title {
			return nil, fmt.Errorf("%s: conflicting @title annotations", value.Path())
		}
		result.Title = title
	}
	switch value.IncompleteKind() {
	case cue.StructKind:
		fields, err := value.Fields(cue.Optional(true))
		if err != nil {
			return nil, err
		}
		result.Properties = map[string]*metadata{}
		for fields.Next() {
			name := fields.Selector().Unquoted()
			child, err := describe(fields.Value(), depth+1)
			if err != nil {
				return nil, err
			}
			result.Order = append(result.Order, name)
			result.Properties[name] = child
		}
	case cue.ListKind:
		item := value.LookupPath(cue.MakePath(cue.AnyIndex))
		if item.Exists() {
			child, err := describe(item, depth+1)
			if err != nil {
				return nil, err
			}
			result.Items = child
		}
	}
	return result, nil
}

func export(name string, value cue.Value) (map[string]any, error) {
	if err := value.Err(); err != nil {
		return nil, fmt.Errorf("%s: %w", name, err)
	}
	expression, err := jsonschema.Generate(value, nil)
	if err != nil {
		return nil, fmt.Errorf("%s: native generation: %w", name, err)
	}
	data, err := value.Context().BuildExpr(expression).MarshalJSON()
	if err != nil {
		return nil, err
	}
	meta, err := describe(value, 0)
	if err != nil {
		return nil, err
	}
	return map[string]any{"schema": json.RawMessage(data), "metadata": meta}, nil
}

func main() {
	definition := flag.String("definition", "", "CUE definition to export")
	flag.Parse()
	if len(flag.Args()) != 1 {
		fail(fmt.Errorf("specify one CUE package directory"))
	}
	path, err := filepath.Abs(flag.Args()[0])
	if err != nil {
		fail(err)
	}
	// Loading loose files bypasses module language settings in upstream CUE.
	// Load the package so its declared language version governs compilation.
	instances := load.Instances([]string{"."}, &load.Config{Dir: path})
	if *definition == "" || len(instances) != 1 {
		fail(fmt.Errorf("specify one -definition and one CUE package"))
	}
	if instances[0].ModuleFile == nil || instances[0].ModuleFile.Language == nil {
		fail(fmt.Errorf("source must declare a CUE module language version"))
	}
	ctx := cuecontext.New()
	value := ctx.BuildInstance(instances[0]).LookupPath(cue.ParsePath(*definition))
	result, err := export(*definition, value)
	if err != nil {
		fail(err)
	}
	info, ok := debug.ReadBuildInfo()
	if !ok {
		fail(fmt.Errorf("CUE build information is unavailable"))
	}
	version := ""
	for _, dependency := range info.Deps {
		if dependency.Path == "cuelang.org/go" && dependency.Replace == nil {
			version = dependency.Version
		}
	}
	if version == "" {
		fail(fmt.Errorf("an unreplaced version of cuelang.org/go is required"))
	}
	result["generator"] = map[string]string{
		"cue_module_version":   version,
		"cue_language_version": instances[0].ModuleFile.Language.Version,
	}
	var sourceFiles []string
	for _, file := range instances[0].BuildFiles {
		sourceFiles = append(sourceFiles, file.Filename)
	}
	result["source_files"] = sourceFiles
	encoder := json.NewEncoder(os.Stdout)
	encoder.SetEscapeHTML(false)
	if err := encoder.Encode(result); err != nil {
		fail(err)
	}
}

func fail(err error) {
	fmt.Fprintln(os.Stderr, err)
	os.Exit(1)
}
