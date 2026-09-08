// This executable checks upstream exporter options on isolated test sources.
package main

import (
	"flag"
	"fmt"
	"os"

	"cuelang.org/go/cue"
	"cuelang.org/go/cue/cuecontext"
	"cuelang.org/go/cue/load"
	"cuelang.org/go/encoding/jsonschema"
	"cuelang.org/go/encoding/openapi"
)

func main() {
	name := flag.String("schema", "", "definition to export")
	evaluate := flag.Bool("eval", false, "call Value.Eval before generation")
	checkValueError := flag.Bool("check-value-error", false, "reject Value.Err before generation, including incomplete errors")
	explicitOpen := flag.Bool("explicit-open", false, "JSON Schema ExplicitOpen setting")
	useOpenAPI := flag.Bool("openapi", false, "use OpenAPI generation")
	expandReferences := flag.Bool("expand-references", false, "OpenAPI ExpandReferences setting")
	strictFeatures := flag.Bool("strict-features", false, "OpenAPI StrictFeatures setting")
	version := flag.String("version", "", "OpenAPI version")
	flag.Parse()
	instances := load.Instances(flag.Args(), nil)
	if len(instances) != 1 {
		fail(fmt.Errorf("expected exactly one CUE instance"))
	}
	ctx := cuecontext.New()
	value := ctx.BuildInstance(instances[0])
	if *name != "" {
		value = value.LookupPath(cue.ParsePath(*name))
	}
	if *checkValueError {
		if err := value.Err(); err != nil {
			fail(err)
		}
	}
	if *evaluate {
		value = value.Eval()
	}
	var output cue.Value
	if *useOpenAPI {
		file, err := openapi.Generate(value, &openapi.Config{
			ExpandReferences: *expandReferences,
			StrictFeatures:   *strictFeatures,
			Version:          *version,
		})
		if err != nil {
			fail(err)
		}
		output = ctx.BuildFile(file)
	} else {
		expr, err := jsonschema.Generate(value, &jsonschema.GenerateConfig{ExplicitOpen: *explicitOpen})
		if err != nil {
			fail(err)
		}
		output = ctx.BuildExpr(expr)
	}
	data, err := output.MarshalJSON()
	if err != nil {
		fail(err)
	}
	if _, err := os.Stdout.Write(append(data, '\n')); err != nil {
		fail(err)
	}
}

func fail(err error) {
	fmt.Fprintln(os.Stderr, err)
	os.Exit(1)
}
