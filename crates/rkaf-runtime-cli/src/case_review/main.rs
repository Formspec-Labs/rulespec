//! Compares recorded rule versions against a local Rulespec policy.
// Rust guideline compliant 2026-02-21

mod case;
mod evidence;
mod policy;
mod report;

use std::io::{self, Write};
use std::path::{Path, PathBuf};

use anyhow::{Context, Result};
use clap::{Args, Parser, Subcommand, ValueEnum};
use policy::{Policy, PolicyOverrides};
use report::{compare, write_report, Report};
use serde::{de::DeserializeOwned, Serialize};

#[derive(Debug, Parser)]
#[command(
    version,
    about = "Compare recorded rule versions against a local Rulespec policy"
)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Subcommand)]
enum Command {
    /// Import a CSV and write an offline case comparison.
    Compare(Compare),
    /// Read one saved case without its batch and shared archive.
    Case {
        /// JSON produced by compare or saved from the batch browser report.
        #[arg(long)]
        report: PathBuf,
        /// Exact case ID from the saved comparison.
        #[arg(long)]
        case_id: Option<String>,
        /// Saved record number. Use this to disambiguate duplicate case IDs.
        #[arg(long)]
        record_number: Option<usize>,
        /// Output format for the one-case view.
        #[arg(long, value_enum, default_value = "json")]
        format: CaseFormat,
    },
    /// Resolve the receipt reference within a single-case JSON file.
    Evidence {
        /// JSON produced by the case command or its browser view.
        #[arg(long)]
        case_record: PathBuf,
        /// The opaque filing receipt reference carried by this case.
        #[arg(long)]
        reference: String,
    },
    /// Export a saved report with analyst dispositions.
    Export {
        /// JSON downloaded from the report view.
        #[arg(long)]
        report: PathBuf,
        /// New directory for the exported report.
        #[arg(long)]
        out: PathBuf,
    },
}

#[derive(Clone, Copy, Debug, ValueEnum)]
enum CaseFormat {
    Json,
    Html,
    Text,
}

#[derive(Debug, Args)]
struct Compare {
    /// Rulespec policy graph or a point-in-time behavior fixture.
    #[arg(long)]
    policy: PathBuf,
    /// Selection settings for the exact policy bytes.
    #[arg(long)]
    selection: Option<PathBuf>,
    /// Optional proposed Rulespec policy to evaluate against the same cases.
    #[arg(long)]
    proposed: Option<PathBuf>,
    /// Selection settings for the proposed policy.
    #[arg(long, requires = "proposed")]
    proposed_selection: Option<PathBuf>,
    /// Retained assertion ID at the start of the rule history.
    #[arg(long)]
    subject: Option<String>,
    /// Evaluation anchor, for example rkaf:applicationSubmissionTime.
    #[arg(long)]
    anchor: Option<String>,
    /// BridgeConsumerRegistration ID.
    #[arg(long)]
    consumer: Option<String>,
    /// Review time as an RFC 3339 timestamp.
    #[arg(long)]
    as_of: Option<String>,
    /// UTF-8 CSV with a header.
    #[arg(long)]
    cases: PathBuf,
    /// JSON object mapping the report field names to CSV headers.
    #[arg(long)]
    map: Option<PathBuf>,
    /// Curated directory of local text or Markdown filing evidence.
    #[arg(long)]
    evidence_dir: Option<PathBuf>,
    /// Plain name of the filing event defined by the approved policy.
    #[arg(long)]
    filing_event: Option<String>,
    /// Time zone used for the reported local dates, such as America/New_York.
    #[arg(long)]
    time_zone: Option<String>,
    /// New directory for the report.
    #[arg(long)]
    out: PathBuf,
}

fn run_compare(args: Compare) -> Result<()> {
    let overrides = PolicyOverrides {
        subject: args.subject.as_deref(),
        anchor: args.anchor.as_deref(),
        consumer: args.consumer.as_deref(),
        as_of: args.as_of.as_deref(),
    };
    let baseline = Policy::read(&args.policy, args.selection.as_deref(), &overrides)?;
    let proposed = args
        .proposed
        .as_ref()
        .map(|path| Policy::read(path, args.proposed_selection.as_deref(), &overrides))
        .transpose()?;
    let report = compare(
        &args.cases,
        args.map.as_deref(),
        args.evidence_dir.as_deref(),
        &baseline,
        proposed.as_ref(),
        case::CaseContext {
            filing_event: args.filing_event,
            time_zone: args.time_zone,
        },
    )?;
    save(&report, &args.out)
}

fn save(report: &Report, out: &Path) -> Result<()> {
    write_report(report, out).with_context(|| format!("Write report to {}", out.display()))?;
    println!("Reviewed {} case row(s).", report.rows.len());
    println!("Open {}", out.join("index.html").display());
    Ok(())
}

fn read_json<T: DeserializeOwned>(path: &Path) -> Result<T> {
    let bytes = std::fs::read(path).with_context(|| format!("Read {}", path.display()))?;
    serde_json::from_slice(&bytes).with_context(|| format!("Parse {}", path.display()))
}

fn print_json(value: &impl Serialize) -> Result<()> {
    let mut output = io::stdout().lock();
    serde_json::to_writer(&mut output, value)?;
    writeln!(output)?;
    Ok(())
}

fn main() -> Result<()> {
    match Cli::parse().command {
        Command::Compare(args) => run_compare(args),
        Command::Case {
            report,
            case_id,
            record_number,
            format,
        } => {
            let report = read_json(&report)?;
            let row = case::select(&report, case_id.as_deref(), record_number)?;
            let excerpt = case::excerpt(&report, row);
            match format {
                CaseFormat::Json => print_json(&excerpt),
                CaseFormat::Html => Ok(print!("{}", case::html(&excerpt)?)),
                CaseFormat::Text => Ok(println!("{}", excerpt.explanation)),
            }
        }
        Command::Evidence {
            case_record,
            reference,
        } => {
            let excerpt = read_json(&case_record)?;
            print_json(case::resolve(&excerpt, &reference)?)
        }
        Command::Export { report, out } => save(&read_json(&report)?, &out),
    }
}
