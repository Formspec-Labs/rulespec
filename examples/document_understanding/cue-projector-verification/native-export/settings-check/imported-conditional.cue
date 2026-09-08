package test

#Conditional: {
	@jsonschema(schema="https://json-schema.org/draft/2020-12/schema")

	matchIf({
		kind!: "ai"
		...
	}, {
		lineage!: _
		...
	}, _) & close({
		kind!:    "human" | "ai"
		lineage?: string
	})
}
