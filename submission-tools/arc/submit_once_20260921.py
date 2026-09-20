"""One authorized ARC upload; credentials stay inside the GitHub runner.
Reads identity/eligibility, submits once, then performs bounded read-only polling.
No authentication responses, headers or raw CLI output are published.
"""
import hashlib
import json
import math
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

SLUG = 'arc-white-box-estimation-challenge-2026'
BASE = 'https://www.aicrowd.com/api/v1'
secret = os.environ.get('AICROWD_API_KEY', '').strip()
out = Path('dist/submission-attempt.json')
receipt = {'state': 'not_attempted', 'accepted_submission_id': None,
           'archive_sha256': hashlib.sha256(Path('dist/submission.tar.gz').read_bytes()).hexdigest(),
           'automatic_upload_retry': False}


def save():
    out.write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt), flush=True)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


opener = urllib.request.build_opener(NoRedirect)


def read_api(path):
    request = urllib.request.Request(BASE + path, headers={'Authorization': 'Token ' + secret,
                                                         'Accept': 'application/json'})
    with opener.open(request, timeout=20) as response:
        data = json.load(response)
    if not isinstance(data, dict):
        raise ValueError('Unexpected JSON shape')
    return data.get('data', data) if isinstance(data.get('data'), dict) else data


if not secret:
    receipt.update(state='blocked_before_upload', reason='repository_secret_missing')
    save()
    raise SystemExit(1)

try:
    identity = read_api('/api_user')
    receipt['identity_verified'] = isinstance(identity.get('id'), int)
    if not receipt['identity_verified']:
        raise ValueError('Identity not confirmed')
    eligibility = read_api('/challenges/' + SLUG + '/eligibility')
    receipt['eligibility'] = {k: eligibility[k] for k in
        ('submissions_allowed', 'rules_accepted', 'participation_terms_accepted')
        if isinstance(eligibility.get(k), bool)}
    denied = eligibility.get('denied_reason')
    if isinstance(denied, str) and re.fullmatch(r'[a-zA-Z0-9_ -]{1,100}', denied):
        receipt['denied_reason'] = denied
    if eligibility.get('submissions_allowed') is not True:
        receipt.update(state='blocked_before_upload', reason='platform_did_not_authorize_submission')
        save()
        raise SystemExit(1)
except urllib.error.HTTPError as error:
    receipt.update(state='blocked_before_upload', reason='preflight_http_error', http_status=error.code)
    save()
    raise SystemExit(1)
except Exception as error:
    receipt.update(state='blocked_before_upload', reason='preflight_failed', error_type=type(error).__name__)
    save()
    raise SystemExit(1)

# Record the uncertain state before the sole mutating CLI invocation.
receipt.update(state='upload_started_outcome_not_yet_known')
save()
try:
    result = subprocess.run(
        ['whest', 'submit', 'dist/submission.tar.gz', '--json', '--description',
         'Fixed 50/50 covariance and orthogonal-sphere hybrid. AI-assisted under account-owner authorization; upstream covariance attribution retained.'],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, timeout=150, check=False)
except subprocess.TimeoutExpired:
    receipt.update(state='unknown_after_timeout_do_not_retry', reason='Inspect AIcrowd before any further upload.')
    save()
    raise SystemExit(1)

text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', result.stdout)
urls = sorted(set(re.findall(r'https://(?:www\.)?aicrowd\.com/challenges/' + SLUG + r'/submissions/[0-9]+', text)))
ids = {int(u.rsplit('/', 1)[1]) for u in urls}
ids.update(int(i) for i in re.findall(r'"submission_id"\s*:\s*([0-9]+)', text))
receipt.update(exit_code=result.returncode, receipt_urls=urls)
if result.returncode != 0 or len(ids) != 1:
    receipt['state'] = 'command_finished_without_unambiguous_receipt_do_not_retry'
    codes = re.findall(r'"code"\s*:\s*"([A-Za-z0-9_:-]{1,80})"', text)
    if codes:
        receipt['cli_error_codes'] = sorted(set(codes))
    save()
    raise SystemExit(1)

submission_id = next(iter(ids))
receipt.update(state='cli_receipt_observed_platform_verification_pending',
               accepted_submission_id=submission_id,
               submission_url='https://www.aicrowd.com/challenges/' + SLUG + '/submissions/' + str(submission_id))
save()
# Read-only polling never uploads another archive, even on API failures.
for attempt in range(10):
    try:
        status = read_api('/submissions/' + str(submission_id))
        reported_id = status.get('submission_id', status.get('id'))
        if reported_id is not None and str(reported_id) != str(submission_id):
            raise ValueError('Submission ID mismatch')
        grading = status.get('grading_status_cd', status.get('grading_status'))
        allowed = {'ready', 'submitted', 'initiated', 'graded', 'failed'}
        receipt['platform_record_verified'] = True
        receipt['state'] = 'platform_submission_record_verified'
        if grading in allowed:
            receipt['grading_status'] = grading
        for key in ('score', 'score_secondary'):
            value = status.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
                receipt[key] = value
        receipt['status_checks'] = attempt + 1
        save()
        if grading in {'graded', 'failed'}:
            break
    except urllib.error.HTTPError as error:
        receipt['last_status_http_error'] = error.code
        save()
    except Exception as error:
        receipt['last_status_error_type'] = type(error).__name__
        save()
    if attempt < 9:
        time.sleep(10)
