# WebOps contracts

`site-profile.v1` generalizes Agency Runner's local site identity without
creating a credential store. It adds normalized capability families,
integration availability, explicit credential environment references, and a
default permission mode. Existing Agency Runner profiles remain valid in their
own workflow; adapters should map them into this contract rather than create a
third profile shape.

`finding.v1` gives recurring agents stable identities based on agent/check,
normalized target, and normalized issue identity. It supports NEW, PERSISTENT,
RESOLVED, REGRESSED, and REOPENED. `history-record.v1` intentionally separates
recommendation, action, and outcome. Consumers ignore unknown additive fields;
breaking changes require a new schema family.

Portable history layout:

```text
.webops/
  profile/ baselines/ siteprobe/ search/ analytics/ contentgraph/
  content/ performance/ accessibility/ ai-visibility/
  reports/ findings/ actions/
```

Credentials are referenced by environment-variable name and never stored.
