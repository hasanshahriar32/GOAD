# Relational realization of the identity subtask

This is a proof argument for the projected identity contract, not a new query-answering theorem or a machine-checked verification of SQLite.

For a finite set of valid `Observation` records, use the same public canonicalization of issuer and certificate identifiers, and the same explicit template aliases. Set every time interval to `[0,0]` and supply no mutation windows. The compared output is `(status, candidate IDs, resolved issuance ID)` for each authentication. Exposure, principal-alias/SID reasoning, temporal attribution and the update-notification API are outside this statement.

Under these conditions, `sql_lineage.SQLiteLineage(method="guarded")` and the identity projection of `engine.LineageEngine` yield the same compared output after each insertion or removal.

1. A profile exists for each successful issuance. The SQL `facts` relation includes that issuance and exactly the bridges with a nonempty, equal canonical issuer and a nonempty, equal request ID. This is the same scoped enrichment as the reference's bridge index. Empty namespaces do not create a cross-source join.
2. For each identity field, the nonempty SQL fact values are precisely the profile's value set. Distinct nonempty template and principal values also agree after the declared alias map. The SQL distinct-value conflict predicate is therefore the profile conflict predicate.
3. The aggregate `known` and `match` flags express whether a value set is nonempty and contains the authentication value. Their Boolean combinations implement the same conjunctive mismatch, shared identifier and strong-match predicates. SKID alone does not become a strong certificate identifier.
4. Both methods reject a known issuer mismatch. A normal profile is a candidate if not contradicted; a conflicting profile remains relevant when it shares an identifier or is not contradicted. Incomplete normal profiles therefore remain candidates in both methods.
5. The reference's possible-order test never excludes a profile in this projection, and its definite-order test always holds, because both event intervals are `[0,0]`. This fact is essential: the statement does not extend to arbitrary real timestamps without adding the temporal predicates.
6. The status priority agrees: failed/unknown authentication, unsupported preauthentication, relevant conflicting evidence, no candidate, missing authentication identifiers, multiple candidates, insufficient identity, and then resolution. Candidate ID ordering and the unique selected issuance therefore agree.
7. Each insertion/removal produces another finite observation set. Applying the preceding steps to each set establishes snapshot equality throughout a history. A caller computing retractions by comparing consecutive snapshots obtains equal retraction decisions. This does not claim the two classes have identical notification or checkpoint APIs.

The frozen empirical comparison checks 5,423 evaluated prefixes across 1,470 histories, with 16,269 prediction rows independently rechecked. This is supporting implementation evidence, not an exhaustive proof over every possible input.

The ordinary `strong_join` query deliberately asks the narrower correlation question: return strong, nonconflicting matches and resolve a unique result among those matches. It does not retain every incomplete possible issuance. Its different coverage is a task-contract distinction, not evidence that a database cannot express the guarded contract.

The projected study retains chronology-negative and consistently forged controls. Erasing time can accept an impossible issuance-to-authentication order. Agreement between implementations cannot authenticate a source or establish real-world causation.
