# rkaf — the Rulespec SDK umbrella crate

One dependency for the Rulespec stack: vocabulary types, compiled constraint
validation, the Layer 4 projectors and the runtime behind one facade.

```toml
[dependencies]
rkaf = { git = "https://github.com/formspec/rulespec" }
```

## Validate a document

```rust
use serde_json::Value;

let document: Value = serde_json::from_str(your_json).expect("parse");
match rkaf::parse_and_validate(&document) {
    Ok(()) => println!("conformant"),
    Err(violations) => {
        for violation in violations {
            eprintln!("{}", violation);
        }
    }
}
```

`parse_and_validate` returns every violation, not the first; the errors carry
the offending JSON pointer and the violated constraint.

## Attach an overlay

```rust
use rkaf::projectors::{JsonLdProjector, Projector};

let projector = JsonLdProjector::with_repo_root("path/to/repo");
let native: serde_json::Value = serde_json::json!({"dcterms:title": "Example"});
let overlay: serde_json::Value = serde_json::json!({"rkaf:assertionOrigin": "rkaf:agent"});
let merged = projector.attach(native, overlay).await?;
```

The three carriers — `JsonSchemaProjector`, `JsonLdProjector`,
`OpenApiProjector` — implement the same `Projector` trait
(`attach` / `extract` / `round_trip` / `validate` / `derive`).

## Registry operations

`rkaf::registries` is a stub: every operation returns
`RegistryUnavailable` until Plan 4 (Layer 3 registries) lands. The surface is
stable; the implementation is not yet.
