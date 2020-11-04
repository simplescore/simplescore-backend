# Score submission API flow

Client submits a score to the server by giving the chart hash and score details.

Server stores score (as a Score if the chart already exists, or a PartialScore if not), then responds with success,
possibly including a request for upload of the chart.

When chart is uploaded, any PartialScore with that chart hash is automatically turned into a Score.
