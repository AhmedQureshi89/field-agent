# Production rules we set

Browser agent limits: at most four actions per run, navigation only, never submit a form, never sign in, verify the page title in code before trusting a result.

Tracing: every model call and tool call is a span inside one trace per user task. Spans carry a trace id, a name and a duration in milliseconds.

Evaluation gate: the offline test set must pass at 67 percent or higher before a deploy. Failures seen online are added to the offline set.

Cost: route short simple questions to the small model, cache repeated questions, cap concurrency and retry with backoff.
