# -*- coding: utf-8 -*-

import requests
import sys
import time
import os
import random
from termcolor import colored

COLORS = {
    "pass": "green",
    "fail": "red",
}

SYMBOLS = {
    "pass": "✔",
    "fail": "✖",
}

def main():
    trigger_url = sys.argv[1]
    trigger_resp = requests.get(trigger_url)

    if trigger_resp.ok:
        trigger_json = trigger_resp.json().get("data", {})

        test_runs = trigger_json.get("runs", [])

        print "Started {} test runs!".format(len(test_runs))

        results = {}
        while len(results.keys()) < len(test_runs):
            time.sleep(1)

            for run in test_runs:
                test_run_id = run.get("test_run_id")
                if not test_run_id in results:
                    result = _get_result(run)
                    if result and result.get("result") in ["pass", "fail"]:
                        results[test_run_id] = result
                        print "{} {}/{} {}".format(
                            colored(result['result'].upper(), COLORS[result['result']]),
                            len(results),
                            len(test_runs),
                            colored('({})'.format(test_run_id), 'white', attrs=['dark']),
                        )
                        for request in result.get("requests"):
                            if not request.get("url"):
                                continue
                            print "  {} {}".format(colored(request['method'], COLORS[request['result']]), colored(request['url'], 'white', attrs=['dark']))
                            for assertion in request.get("assertions"):
                                res = colored(SYMBOLS[assertion['result']], COLORS[assertion['result']])
                                lhs = str(assertion['property'] or assertion['target_value']).encode('utf-8')
                                cmp = colored(assertion['comparison'], 'white', attrs=['bold'])
                                actual_value = assertion['actual_value'].encode('utf-8')
                                print "    {res} {lhs} {cmp} {actual_value}".format(lhs=lhs, cmp=cmp, res=res, actual_value=actual_value)
                                if assertion['error']:
                                    print "      {}".format(colored(assertion['error'], 'yellow', attrs=['bold']))


        pass_count = sum([r.get("result") == "pass" for r in results.values()])
        fail_count = sum([r.get("result") == "fail" for r in results.values()])

        if fail_count > 0:
            print "{} test runs passed. {} test runs failed.".format(pass_count, fail_count)
            exit(1)

        print "All test runs passed."


def _get_result(test_run):
    # generate Personal Access Token at https://www.runscope.com/applications
    if not "RUNSCOPE_ACCESS_TOKEN" in os.environ:
        print "Please set the environment variable RUNSCOPE_ACCESS_TOKEN. You can get an access token by going to https://www.runscope.com/applications"
        exit(1)

    API_TOKEN = os.environ["RUNSCOPE_ACCESS_TOKEN"]

    opts = {
        "base_url": "https://api.runscope.com",
        "bucket_key": test_run.get("bucket_key"),
        "test_id": test_run.get("test_id"),
        "test_run_id": test_run.get("test_run_id")
    }
    result_url = "{base_url}/buckets/{bucket_key}/tests/{test_id}/results/{test_run_id}".format(**opts)

    headers = {
        "Authorization": "Bearer {}".format(API_TOKEN),
        "User-Agent": "python-trigger-sample"
    }
    result_resp = requests.get(result_url, headers=headers)

    if result_resp.ok:
        return result_resp.json().get("data")

    return None


if __name__ == '__main__':
    time.sleep(random.randint(30, 120))
    main()
