# Changelog

## Unreleased

- Complete the retrospective Boltz-2 / 8XTC benchmark with ten predeclared seeds.
- Include all ten predicted complexes, the experimental reference, the compressed
  fixed MSA, per-seed metrics, confidence, provenance and compact job logs.
- Report all samples and aggregate statistics; add protein-aligned ligand figures
  and compare model confidence with experimental pose error.
- Match proteins by mmCIF polymer sequence position and reconstruct Boltz's all-X
  ModelCIF canonical sequences from the complete polymer monomer table.
- Reject incomplete ligand atom mappings and differing protein constructs.
- Correct position 190 handling: the deposited construct has ALA190, so its CB
  distance is a positional marker, not catalytic serine hydroxyl geometry.
- Support stored-MSA inference and evaluation-only recovery without repeating
  an already completed GPU calculation.
- Add offline evaluator regression tests, saved-artifact verification and CI checks.
- Document limitations, Hyperion test batches, CPU reproduction and data inventory.
