from datetime import datetime
import os

def generate_html_report(question, response, evaluation, evaluation_time):

    metrics_rows = ""

    for metric in evaluation["metrics"]:

        status = "PASS" if metric["passed"] else "FAIL"
        color = "#28a745" if metric["passed"] else "#dc3545"

        metrics_rows += f"""
        <tr>
            <td>{metric['metric']}</td>
            <td>{metric['score']}</td>
            <td>{metric['threshold']}</td>
            <td style="color:{color};font-weight:bold;">{status}</td>
            <td>{metric['reason']}</td>
        </tr>
        """

    overall = "PASS" if evaluation["overall_passed"] else "FAIL"
    overall_color = "#28a745" if evaluation["overall_passed"] else "#dc3545"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>AI Chatbot Evaluation Report</title>

<style>

body {{
    font-family: Arial, sans-serif;
    background:#f4f6f9;
    margin:40px;
}}

.header {{
    background: linear-gradient(135deg, #1f4e79, #355C7D);
    color: white;
    padding: 35px;
    text-align: center;
    border-radius: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.2);
}}

.header h1 {{
    margin: 0;
    font-size: 42px;
    font-weight: bold;
}}

.header p {{
    margin-top: 12px;
    font-size: 18px;
    opacity: 0.95;
}}

.card {{
    background:white;
    padding:20px;
    margin-top:20px;
    border-radius:8px;
    box-shadow:0 2px 8px rgba(0,0,0,0.1);
}}

.question-card {{
    background:#E8F4FD;
    border-left:8px solid #2196F3;
    border-radius:18px;
}}

.response-card {{
    background:#E8F5E9;
    border-left:8px solid #4CAF50;
    border-radius:18px;
}}

.result-card {{
    background:#FFF3E0;
    border-left:8px solid #FF9800;
    border-radius:18px;
}}

.metrics-card {{
    background:#F3E5F5;
    border-left:8px solid #9C27B0;
    border-radius:18px;
}}

table {{
    width:100%;
    border-collapse:collapse;
}}

th {{
    background:#1f4e79;
    color:white;
    padding:10px;
}}

td {{
    padding:10px;
    border:1px solid #ddd;
}}

tr:nth-child(even){{
    background:#f8f8f8;
}}

.badge {{
    display:inline-block;
    padding:8px 15px;
    color:white;
    font-weight:bold;
    border-radius:20px;
}}

.summary-container{{
    display:flex;
    gap:20px;
    margin-top:25px;
    margin-bottom:25px;
}}

.summary-card{{
    flex:1;
    background:white;
    border-radius:12px;
    padding:20px;
    text-align:center;
    box-shadow:0 3px 8px rgba(0,0,0,.1);
}}

.summary-title{{
    font-size:15px;
    color:#666;
    font-weight:bold;
}}

.summary-value{{
    margin-top:10px;
    font-size:24px;
    font-weight:bold;
    color:#1f4e79;
}}

.time-card{{
    background:#E3F2FD;
    border-top:6px solid #2196F3;
}}

.guardrail-card{{
    background:#E8F5E9;
    border-top:6px solid #4CAF50;
}}

.result-summary-card{{
    background:#FFF8E1;
    border-top:6px solid #FFC107;
}}

.judge-card{{
    background:#F3E5F5;
    border-top:6px solid #9C27B0;
}}

.time-card .summary-value{{
    color:#1976D2;
}}

.guardrail-card .summary-value{{
    color:#2E7D32;
}}

.result-summary-card .summary-value{{
    color:#F57C00;
}}

.judge-card .summary-value{{
    color:#7B1FA2;
}}

</style>

</head>

<body>

<div class="header">

    <h1>🤖 AI Chatbot Response Evaluation Dashboard</h1>

    <p>
        Powered by DeepEval • Planit Amplify Judge • JSON Knowledge Base
    </p>

    <p>
        Report Generated :
        {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
    </p>

</div>
<div class="summary-container">

     <div class="summary-card judge-card">
            <div class="summary-title">🤖 Judge Model</div>
            <div class="summary-value">Planit Amplify</div>
        </div>

    <div class="summary-card guardrail-card">
        <div class="summary-title">🛡 Guardrail</div>
        <div class="summary-value">PASSED</div>
    </div>

    <div class="summary-card result-summary-card">
        <div class="summary-title">📊 Overall Result</div>
        <div class="summary-value">{overall}</div>
    </div>

    <div class="summary-card time-card">
            <div class="summary-title">⏱ Evaluation Time</div>
            <div class="summary-value">{evaluation_time} ms</div>
    </div>

   

</div>

<div class="card question-card">
<h2>❓ User Question</h2>
<p>{question}</p>
</div>

<div class="card response-card">
<h2>🤖 Chatbot Response</h2>
<p>{response}</p>
</div>

<div class="card result-card">
<h2>📊 Overall Evaluation</h2>
<span class="badge" style="background:{overall_color};">
    {overall}
</span>
</div>

<div class="card metrics-card">
<h2>📈 Evaluation Metrics</h2>

<table>

<tr>
<th>Metric</th>
<th>Score</th>
<th>Threshold</th>
<th>Status</th>
<th>Reason</th>
</tr>

{metrics_rows}

</table>

</div>

</body>

</html>
"""

    os.makedirs("results", exist_ok=True)

    with open(
        "results/chatbot_evaluation_report.html",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(html)