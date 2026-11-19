//! Copies curated filing evidence and locates plain-text passages.
// Rust guideline compliant 2026-02-21

use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};

use anyhow::{ensure, Context, Result};
use serde::{Deserialize, Serialize};

use crate::policy::sha256;

pub type Documents = BTreeMap<String, String>;

#[derive(Debug, Deserialize, Serialize)]
pub struct LocalEvidence {
    pub path: String,
    pub sha256: String,
    pub anchor: Option<String>,
    pub passage: Option<String>,
}

pub struct EvidenceDirectory {
    root: PathBuf,
    paths: BTreeMap<String, Option<String>>,
    pub documents: Documents,
}

impl EvidenceDirectory {
    pub fn open(path: &Path) -> Result<Self> {
        let root = path
            .canonicalize()
            .with_context(|| format!("Open evidence directory {}", path.display()))?;
        ensure!(root.is_dir(), "Choose a directory of local evidence files");
        Ok(Self {
            root,
            paths: BTreeMap::new(),
            documents: BTreeMap::new(),
        })
    }

    pub fn resolve(&mut self, reference: &str) -> Option<LocalEvidence> {
        let (path, anchor) = parse_reference(reference)?;
        let root = &self.root;
        let documents = &mut self.documents;
        let digest = self.paths.entry(path.to_owned()).or_insert_with(|| {
            let file = root.join(path).canonicalize().ok()?;
            if !file.starts_with(root) || !file.is_file() {
                return None;
            }
            let text = fs::read_to_string(file).ok()?;
            let digest = sha256(text.as_bytes());
            documents.entry(digest.clone()).or_insert(text);
            Some(digest)
        });
        let digest = digest.as_ref()?;
        let text = &documents[digest];
        let passage = anchor.and_then(|id| anchored_passage(text, id));
        Some(LocalEvidence {
            path: path.to_owned(),
            sha256: digest.clone(),
            anchor: anchor.map(str::to_owned),
            passage,
        })
    }
}

fn is_safe_token(value: &str) -> bool {
    !value.is_empty()
        && value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b'.'))
}

fn parse_reference(reference: &str) -> Option<(&str, Option<&str>)> {
    let reference = reference.trim();
    let (path, anchor) = reference
        .split_once('#')
        .map_or((reference, None), |(path, anchor)| (path, Some(anchor)));
    if path
        .split('/')
        .any(|part| !is_safe_token(part) || matches!(part, "." | ".."))
        || anchor.is_some_and(|value| !is_safe_token(value))
    {
        return None;
    }
    let extension = Path::new(path).extension()?.to_str()?;
    (extension.eq_ignore_ascii_case("md") || extension.eq_ignore_ascii_case("txt"))
        .then_some((path, anchor))
}

fn explicit_anchor(line: &str) -> Option<&str> {
    let rest = line.trim_start().strip_prefix("<a id=")?;
    let quote = rest.chars().next()?;
    if !matches!(quote, '\'' | '"') {
        return None;
    }
    let (id, rest) = rest[1..].split_once(quote)?;
    (is_safe_token(id) && rest.starts_with('>')).then_some(id)
}

fn heading(line: &str) -> Option<&str> {
    let line = line.trim_start();
    let title = line.trim_start_matches('#');
    ((1..=6).contains(&(line.len() - title.len())) && title.starts_with(' '))
        .then(|| title.trim().trim_end_matches('#').trim_end())
        .filter(|title| !title.is_empty())
}

fn anchored_passage(text: &str, anchor: &str) -> Option<String> {
    let lines: Vec<_> = text.lines().collect();
    let mut explicit = lines
        .iter()
        .enumerate()
        .filter(|(_, line)| explicit_anchor(line) == Some(anchor));
    let start = if let Some((index, _)) = explicit.next() {
        if explicit.next().is_some() {
            return None;
        }
        // Skip the anchor tag and any blank separator before its heading.
        lines[index + 1..]
            .iter()
            .position(|line| !line.trim().is_empty())?
            + index
            + 1
    } else {
        let mut headings = lines.iter().enumerate().filter(|(_, line)| {
            heading(line).is_some_and(|title| {
                title
                    .split_whitespace()
                    .collect::<Vec<_>>()
                    .join("-")
                    .eq_ignore_ascii_case(anchor)
            })
        });
        let (index, _) = headings.next()?;
        if headings.next().is_some() {
            return None;
        }
        index
    };
    let end = lines[start + 1..]
        .iter()
        .position(|line| heading(line).is_some() || explicit_anchor(line).is_some())
        .map_or(lines.len(), |offset| start + offset + 1);
    Some(lines[start..end].join("\n").trim_end().to_owned())
}

pub fn validate(documents: &Documents) -> Result<()> {
    for (digest, text) in documents {
        ensure!(
            sha256(text.as_bytes()) == *digest,
            "Filing evidence bytes differ from digest {digest}"
        );
    }
    Ok(())
}

pub fn copy_path(digest: &str) -> String {
    // The report verifies the digest before using this path for output.
    format!("evidence/{}.txt", digest.trim_start_matches("sha256:"))
}

pub fn write_copies(documents: &Documents, out: &Path) -> Result<()> {
    if documents.is_empty() {
        return Ok(());
    }
    fs::create_dir(out.join("evidence"))?;
    for (digest, text) in documents {
        fs::write(out.join(copy_path(digest)), text.as_bytes())?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{anchored_passage, parse_reference};

    #[test]
    fn permits_only_relative_text_references() {
        assert_eq!(
            parse_reference("archive/filing-records.md#fr-09"),
            Some(("archive/filing-records.md", Some("fr-09")))
        );
        assert_eq!(parse_reference("slip.txt"), Some(("slip.txt", None)));
        for raw in [
            "../secret.md",
            "/private/secret.txt",
            "file:///secret.txt",
            "https://a.org/e.md",
            "urn:record:1",
            "archive/%2E%2E/a.md",
            "archive/../a.md",
            "slip.html",
            "e.md#x#y",
        ] {
            assert_eq!(parse_reference(raw), None, "{raw}");
        }
    }

    #[test]
    fn finds_case_passages_by_heading_or_explicit_id() {
        let text = "### FR-08\nOlder\n\n<a id=\"fr-09\"></a>\n\n### Receipt nine\nReceipt and slip\n\n### FR-10\nLater";
        assert_eq!(
            anchored_passage(text, "fr-09").as_deref(),
            Some("### Receipt nine\nReceipt and slip")
        );
        assert_eq!(
            anchored_passage(text, "fr-10").as_deref(),
            Some("### FR-10\nLater")
        );
        assert_eq!(anchored_passage(text, "fr-99"), None);
        assert_eq!(anchored_passage("### X\nFirst\n### X\nSecond", "x"), None);
    }
}
