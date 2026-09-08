package test

#Conditional: {
	@jsonschema(schema="https://json-schema.org/draft/2020-12/schema")

	matchIf({
		kind!: "ai"
		...
	}, {
		lineage!: _
		...
	}, matchN(0, [null | bool | number | string | [...] | {
		lineage!: _
		...
	}]) & {
		...
	}) & close({
		kind!:    "human" | "ai"
		lineage?: string
	})
}
