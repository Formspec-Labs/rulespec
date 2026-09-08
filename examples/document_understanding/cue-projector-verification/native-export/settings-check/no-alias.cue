package test

// A reusable concept identifier.
#Concept: {
    // Stable identifier. Use it in later references.
    "z_id": string
    // The source label.
    "a_label": string
}

// A composed record.
#Composed: {
    #Concept
    "own": int & >=1
}

#Conditional: {
    kind: "human" | "ai"
    if kind == "ai" {
        // Evidence for the model output.
        "lineage": string
    }
}

#Rich: {
    @title("Rich record")
    @description("Explicit shape description")
    // Adjacent description.
    "text": string @title("Text") @description("Exact source text")
}
