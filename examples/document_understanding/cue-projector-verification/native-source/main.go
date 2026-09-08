// This probe uses upstream CUE parsing to inspect source structure. It does
// not generate constraints or replace the production compiler.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"

	"cuelang.org/go/cue"
	"cuelang.org/go/cue/ast"
	"cuelang.org/go/cue/cuecontext"
	"cuelang.org/go/cue/format"
	"cuelang.org/go/cue/literal"
	"cuelang.org/go/cue/load"
	"cuelang.org/go/cue/parser"
	"cuelang.org/go/encoding/jsonschema"
)

type sourceField struct {
	Path        []string          `json:"path"`
	Line        int               `json:"line"`
	ValueKind   string            `json:"valueKind"`
	Annotations map[string]string `json:"annotations,omitempty"`
}

type sourceReport struct {
	File       string        `json:"file"`
	Fields     []sourceField `json:"fields"`
	Conditions []string      `json:"conditions"`
}

func inspect(path string) (sourceReport, error) {
	report := sourceReport{File: path, Fields: []sourceField{}, Conditions: []string{}}
	file, err := parser.ParseFile(path, nil, parser.ParseComments)
	if err != nil {
		return report, err
	}
	var fieldPath []string
	ast.Walk(file, func(node ast.Node) bool {
		switch node := node.(type) {
		case *ast.Field:
			name, _, nameErr := ast.LabelName(node.Label)
			if nameErr != nil {
				name = "[pattern]"
			}
			fieldPath = append(fieldPath, name)
			entry := sourceField{
				Path: append([]string{}, fieldPath...), Line: node.Pos().Line(),
				ValueKind: fmt.Sprintf("%T", node.Value), Annotations: map[string]string{},
			}
			var docs []string
			for _, comment := range ast.Comments(node) {
				if comment.Doc || comment.Line {
					docs = append(docs, strings.TrimSpace(comment.Text()))
				}
			}
			if description := strings.TrimSpace(strings.Join(docs, "\n")); description != "" {
				entry.Annotations["description"] = description
			}
			attrs := append([]*ast.Attribute{}, node.Attrs...)
			if value, ok := node.Value.(*ast.StructLit); ok {
				for _, declaration := range value.Elts {
					if attr, ok := declaration.(*ast.Attribute); ok {
						attrs = append(attrs, attr)
					}
				}
			}
			for _, attr := range attrs {
				key, body := attr.Split()
				if key != "title" && key != "description" {
					continue
				}
				value, attrErr := literal.Unquote(strings.TrimSpace(body))
				if attrErr != nil {
					err = fmt.Errorf("%s: @%s requires a quoted literal: %w", attr.Pos(), key, attrErr)
					continue
				}
				entry.Annotations[key] = value
			}
			report.Fields = append(report.Fields, entry)
		case *ast.IfClause:
			text, formatErr := format.Node(node.Condition)
			if formatErr != nil {
				err = formatErr
			} else {
				report.Conditions = append(report.Conditions, string(text))
			}
		}
		return true
	}, func(node ast.Node) {
		if _, ok := node.(*ast.Field); ok {
			fieldPath = fieldPath[:len(fieldPath)-1]
		}
	})
	return report, err
}

func main() {
	schemaName := flag.String("schema", "", "export this definition with the native Go API")
	explicitOpen := flag.Bool("explicit-open", false, "use GenerateConfig.ExplicitOpen")
	flag.Parse()
	if *schemaName != "" {
		instances := load.Instances(flag.Args(), nil)
		if len(instances) != 1 {
			fmt.Fprintln(os.Stderr, "expected exactly one CUE instance")
			os.Exit(1)
		}
		ctx := cuecontext.New()
		value := ctx.BuildInstance(instances[0]).LookupPath(cue.ParsePath(*schemaName))
		expr, err := jsonschema.Generate(value, &jsonschema.GenerateConfig{ExplicitOpen: *explicitOpen})
		if err == nil {
			var output []byte
			output, err = ctx.BuildExpr(expr).MarshalJSON()
			if err == nil {
				_, err = os.Stdout.Write(append(output, '\n'))
			}
		}
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		return
	}
	encoder := json.NewEncoder(os.Stdout)
	for _, path := range flag.Args() {
		report, err := inspect(path)
		if err == nil {
			err = encoder.Encode(report)
		}
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
}
