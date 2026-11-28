## Which sheet reached the model?

*Source update: November 16, 2026 Pacific; documentation checked November 17 UTC.*

Google’s Gemini API guide says XLS/XLSX input reads only the first worksheet and converts its cell values to CSV, without formulas or formatting. Its November 5 release notes say this processing was unchanged while support for other formats expanded. This is a documented API path, not a GhostMesh execution result or a statement about Docling and Onyx. [Format guide](https://aistudio.google.com/docs/document-processing#office-documents), [release notes](https://aistudio.google.com/docs/changelog#11-05-2026).

A first-sheet route can be sufficient when that is the intended sheet. For a question about another sheet, upload success alone cannot establish coverage. Our GhostMesh judgment is to make the selected sheet explicit, then retain the separate question of whether its values are literal, cached or freshly calculated. Worksheet coverage and value state need separate evidence.

A disposable two-sheet workbook with a different harmless marker on each sheet could check that coverage boundary. It has not been uploaded or tested here. No API call, account-entitlement check or model-output comparison was performed for this update. The original fixture result below remains a separate, limited observation.
