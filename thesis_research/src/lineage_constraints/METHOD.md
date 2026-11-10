# Experimental method and conditional properties

An observation has an immutable source record ID, an event kind, an issuer namespace, optional certificate identifiers, and a time interval `[lower, upper]`. An interval must be a justified bound if a definite conclusion is to be used operationally; a guessed two-second tolerance is only a sensitivity setting. Authentication also carries the observed success result and PKINIT type.

Windows `TimeCreated` is an audit-record timestamp. Converting it into an effective-operation interval additionally requires assumptions about audit delay and clock behavior. The archived-data reader's point and symmetric-error projections are sensitivity inputs. They do not establish those assumptions. `clock_audit.py` checks whether controlled operation brackets can falsify a supplied clock/audit-delay model; the live pilot does falsify its pre-capture constant-offset model. The workflow therefore withholds a guaranteed temporal claim even though a conditional engine run returns a resolved overlap.

The task is to identify a captured issuance record that can explain successful certificate authentication. It is narrower than deciding whether an ADCS exploit succeeded or identifying a necessary enabling mutation.

## Candidate construction

CA database enrichment uses `(issuer, request_id)`. Missing direct fields can be filled, but conflicting nonempty observations are retained as a conflict rather than overwritten. A template name/OID alias is used only when provided explicitly. SKID can recur when a public key is reused; it cannot independently establish certificate identity.

For issuance `c` and authentication `a`, a candidate is excluded if any known identity field contradicts the corresponding field or if `c.lower > a.upper`. An incompletely identified issuance is retained as a weak candidate when no known field contradicts it. This prevents the disappearance of incomplete observations from manufacturing a unique answer.

A strong shared identifier is an observed certificate thumbprint or a serial in a known matching issuer namespace. Serial comparison removes presentation padding but does not remove issuer scope. Thumbprints are identifiers in this model; this code neither verifies a certificate signature nor authenticates log sources.

A definite resolved link requires successful certificate authentication, exactly one consistent candidate with strong shared identity, no relevant conflicting bridge profile, and `c.upper <= a.lower`. Otherwise the output retains the possible candidate set and a reason for abstention. Conclusions are always relative to the retained observations and declared assumptions.

## Mutation overlap

Given an exact template match and a recorded mutation window with opening interval `O` and closing interval `R`, the issuance definitely overlaps when

```
O.upper <= c.lower  and  c.upper <= R.lower.
```

It possibly overlaps when the timestamp boxes admit some `open <= issuance <= close`. The implemented possible check is `O.lower <= c.upper` and `c.lower <= R.upper`, with a feasible opening/closing pair required by the input schema. An observed overlap alone does not establish that the changed attribute enabled an otherwise impossible enrollment. That would require effective permission/state reconstruction and a policy counterfactual.

## Properties under explicit assumptions

1. **No silently accepted contradiction.** A resolved candidate cannot have a known identity-field mismatch, because every such mismatch removes it before the unique-candidate decision. A conflicting scoped bridge profile prevents resolution when relevant. This is a property of this implementation, not a new result about cryptography.
2. **Conditional unique-link soundness.** Assume the true issuance is captured, every recorded identity field and namespace mapping is truthful, strong identity does not collide across distinct physical certificates, and true event times lie inside their intervals. The true issuance remains compatible and temporally feasible. If the engine resolves exactly one compatible candidate, that candidate is the true issuance. Dropped true issuances, consistently forged logs, incorrect aliases, and unbounded clock error violate this premise; the explicit forgery negative control demonstrates the failure.
3. **Definite interval containment.** If the definite-overlap inequalities hold, every assignment inside the three timestamp boxes satisfies `open <= issuance <= close`. This follows by transitivity through `open <= O.upper <= c.lower <= issuance <= c.upper <= R.lower <= close`. Unit tests independently enumerate integer timestamp assignments to check the implementation against this property.
4. **Delivery-order independence of the final retained-evidence answer.** The decision is a deterministic function of the current record set. Replaying a permutation of the same immutable observations therefore yields the same final decision. Intermediate conclusions can change: new evidence may establish a link, add ambiguity, or reveal a contradiction. Updates expose retractions explicitly. The benchmark checks reverse-order replay and checkpoint restoration on every case; the tests also exhaust all permutations of a small case.

These properties require no completeness claim about future or missing observations. A currently resolved link can be withdrawn when additional evidence arrives. The prototype does not announce irreversible online finality, assume a network watermark, or delete history automatically.

## What is not claimed as novelty

Issuer namespaces, consistent entity matching, interval bounds, three-valued reasoning, event sourcing, and provenance are established concepts. The research candidate is their certificate-specific combination for revisable issuance/use and rollback-window attribution, together with a protocol exposing where simple joins produce unjustified definite claims. An application paper would need evidence that this combination solves an operational problem beyond existing temporal rule systems and practical ADCS queries.

## Failure-domain grouping and source-truth falsification

`source_faults.py` considers every subset of up to `f` explicitly named optional-source groups. Dropping a group removes all its bridge records; raw CA/KDC records remain authoritative. A source partition is an input assumption. Copies of the same exporter are not independent origins, and the implementation does not authenticate the partition or the raw logs.

Under correct raw anchors, correct namespace/time bounds, captured true issuance, and at most `f` faulty optional groups, one enumerated hypothesis drops every faulty group. In that hypothesis the true issuance cannot be excluded by a contradictory optional claim. Its candidate therefore occurs in the union. A certain link requires the same resolved link in every hypothesis, including otherwise unresolved or conflicting retained sets. Increasing the budget cannot create certainty merely by selecting a more favorable deletion. This is an application of explicit possible/certain reasoning, not a new general repair theory.

The deterministic correlated-source control contains six false export rows in one failure domain. A two-record budget is outside its own assumption and produces a wrong certain link. A sufficient six-record budget retains the true candidate with 64 hypotheses. The one-source model retains it with two hypotheses and abstains from certainty. Their assumptions differ; the comparison measures the consequence of modeling a common failure boundary, not a universal accuracy advantage.

The second control gives true times `opened=0, closed=1, issued=2`, with bounds `[0,3]` for each variable. A fabricated but jointly consistent `opened <= issued <= closed` channel implies a definite overlap in the reported network while contradicting the latent history. Detecting inconsistent constraints does not authenticate a sensor or reject every false consistent statement. Trusted-order conclusions require that extra source-truth assumption.
