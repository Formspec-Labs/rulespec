//! Compares recorded rule versions against a local Rulespec policy.
// Rust guideline compliant 2026-02-21

mod evidence;
mod policy;
mod report;

use std::path::{Path, PathBuf};

use anyhow::{Context, Result};
use clap::{Args, Parser, Subcommand};
use policy::{Policy, PolicyOverrides};
use report::{compare, write_report, Report};

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
    )?;
    save(&report, &args.out)
}

fn save(report: &Report, out: &Path) -> Result<()> {
    write_report(report, out).with_context(|| format!("Write report to {}", out.display()))?;
    println!("Reviewed {} case row(s).", report.rows.len());
    println!("Open {}", out.join("index.html").display());
    Ok(())
}

fn main() -> Result<()> {
    match Cli::parse().command {
        Command::Compare(args) => run_compare(args),
        Command::Export { report, out } => {
            let saved = std::fs::read(&report)
                .with_context(|| format!("Read report {}", report.display()))?;
            let saved = serde_json::from_slice(&saved)
                .with_context(|| format!("Parse report {}", report.display()))?;
            save(&saved, &out)
        }
    }
}
