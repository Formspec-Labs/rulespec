//! `rkaf-behavior-validate` — Rulespec Layer 5 conformance CLI.
//!
//! Validates `BehaviorTestCase` fixtures against the 5 behavioral contracts
//! in `spec/rkaf-behavior.md`. The conformance reporter shells out to this
//! binary; partner conformance suites can also invoke it directly.
//!
//! Exit codes:
//!   0  every fixture passed (computed output == declared expectedOutput)
//!   1  one or more fixtures failed
//!   2  setup error (file missing, parse failure, malformed test case)

use clap::Parser;
use rkaf_runtime::{Runtime, RuntimeError};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

#[derive(Parser, Debug)]
#[command(
    name = "rkaf-behavior-validate",
    version,
    about = "Validate Rulespec BehaviorTestCase fixtures against Layer 5 contracts",
    long_about = "Reads one or more JSON-LD BehaviorTestCase files and asserts that running each \
through the rkaf-runtime contract dispatcher produces output matching the declared \
rkaf:expectedOutput. Use --evaluate CASE to print the computed JSON verdict for one case.\n\
\n\
Exit codes:\n  \
0  all fixtures match expected output\n  \
1  at least one fixture diverged\n  \
2  setup/parse error"
)]
struct Cli {
    /// Emit a machine-readable JSON envelope on stdout. Default is human table.
    #[arg(long)]
    json: bool,

    /// Print the computed JSON verdict for one case, without an expected answer.
    #[arg(long, value_name = "CASE", conflicts_with_all = ["fixtures", "json"])]
    evaluate: Option<PathBuf>,

    /// Behavior fixture paths to validate.
    #[arg(required_unless_present = "evaluate")]
    fixtures: Vec<PathBuf>,
}

#[derive(Debug)]
struct FixtureVerdict {
    name: String,
    result: String,
    diagnostic: Option<String>,
}

fn read_case(path: &Path) -> Result<Value, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("read {}: {e}", path.display()))?;
    serde_json::from_slice(&bytes).map_err(|e| format!("parse {}: {e}", path.display()))
}

fn evaluate_one(path: &PathBuf) -> FixtureVerdict {
    let name = path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("<unknown>")
        .to_owned();
    let tc = match read_case(path) {
        Ok(value) => value,
        Err(diagnostic) => {
            return FixtureVerdict {
                name,
                result: "error".into(),
                diagnostic: Some(diagnostic),
            }
        }
    };
    // Plan 7e.3 — a fixture MAY declare `rkaf:expectedRuntimeError` to assert
    // the runtime raises a specific structural error (e.g. MalformedTestCase
    // on a dangling IRI). Used for strict-error parity tests where the
    // contract refuses to compute a verdict at all.
    let expected_runtime_error: Option<&str> =
        tc.get("rkaf:expectedRuntimeError").and_then(Value::as_str);

    match (Runtime::evaluate_and_check(&tc), expected_runtime_error) {
        (Ok(_), None) => FixtureVerdict {
            name,
            result: "pass".into(),
            diagnostic: None,
        },
        (Ok(_), Some(expected_err)) => FixtureVerdict {
            name,
            result: "fail".into(),
            diagnostic: Some(format!(
                "expected runtime error {expected_err:?}, got Ok verdict"
            )),
        },
        // OutputMismatch precedence is deliberate: a fixture declaring
        // `rkaf:expectedRuntimeError = "rkaf:OutputMismatch"` is therefore
        // unreachable. OutputMismatch is always treated as an unexpected
        // runtime surprise — fixtures use `rkaf:expectedOutput` for the
        // success path; there is no use case for asserting a mismatch.
        (Err(RuntimeError::OutputMismatch { expected, actual }), _) => FixtureVerdict {
            name,
            result: "fail".into(),
            diagnostic: Some(format!(
                "OutputMismatch:\n  expected: {}\n  actual:   {}",
                serde_json::to_string(&expected).unwrap_or_default(),
                serde_json::to_string(&actual).unwrap_or_default()
            )),
        },
        (Err(other), Some(expected_err)) => {
            let actual_tag = other.iri_tag();
            if actual_tag == expected_err {
                FixtureVerdict {
                    name,
                    result: "pass".into(),
                    diagnostic: Some(format!("expected runtime error matched: {other}")),
                }
            } else {
                FixtureVerdict {
                    name,
                    result: "fail".into(),
                    diagnostic: Some(format!(
                        "expected runtime error {expected_err:?}, got {actual_tag:?}: {other}"
                    )),
                }
            }
        }
        (Err(other), None) => FixtureVerdict {
            name,
            result: "error".into(),
            diagnostic: Some(format!("{other}")),
        },
    }
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    if let Some(path) = cli.evaluate {
        return match read_case(&path)
            .and_then(|case| Runtime::evaluate(&case).map_err(|err| err.to_string()))
        {
            Ok(verdict) => {
                println!("{}", verdict.output);
                ExitCode::SUCCESS
            }
            Err(diagnostic) => {
                eprintln!("{diagnostic}");
                ExitCode::from(2)
            }
        };
    }
    let verdicts: Vec<FixtureVerdict> = cli.fixtures.iter().map(evaluate_one).collect();

    if cli.json {
        let payload = json!({
            "fixtures": verdicts.iter().map(|v| {
                json!({
                    "name": v.name,
                    "result": v.result,
                    "diagnostic": v.diagnostic,
                })
            }).collect::<Vec<_>>(),
        });
        println!("{}", serde_json::to_string(&payload).unwrap());
    } else {
        for v in &verdicts {
            print!("  [{}] {}", v.result.to_uppercase(), v.name);
            if let Some(d) = &v.diagnostic {
                print!("\n    {d}");
            }
            println!();
        }
        let pass = verdicts.iter().filter(|v| v.result == "pass").count();
        println!("\n{pass}/{} fixtures pass", verdicts.len());
    }

    let any_error = verdicts.iter().any(|v| v.result == "error");
    let any_fail = verdicts.iter().any(|v| v.result == "fail");
    if any_error {
        ExitCode::from(2)
    } else if any_fail {
        ExitCode::from(1)
    } else {
        ExitCode::SUCCESS
    }
}
