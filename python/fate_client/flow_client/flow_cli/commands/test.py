#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import time
import traceback

import click

from flow_client.flow_cli.utils import cli_args
from flow_client.flow_cli.utils.cli_utils import prettify
from flow_sdk.client import FlowClient


@click.group(short_help="FATE Flow Test Operations")
@click.pass_context
def test(ctx):
    """
    \b
    Provides numbers of component operational commands, including metrics, parameters and etc.
    For more details, please check out the help text.
    """
    pass


@test.command("toy", short_help="Toy Test Command")
@cli_args.GUEST_PARTYID_REQUIRED
@cli_args.HOST_PARTYID_REQUIRED
@cli_args.TIMEOUT
@cli_args.TASK_CORES
@click.pass_context
def toy(ctx, **kwargs):
    flow_client = FlowClient(ip=ctx.obj["ip"], port=ctx.obj["http_port"], version=ctx.obj["api_version"],
                             app_key=ctx.obj.get("app_key"), secret_key=ctx.obj.get("secret_key"))
    submit_result = flow_client.test.toy(**kwargs)
    if submit_result["retcode"] == 0:
        for t in range(kwargs["timeout"]):
            job_id = submit_result["jobId"]
            r = flow_client.job.query(job_id=job_id, role="guest", party_id=kwargs["guest_party_id"])
            if r["retcode"] == 0 and len(r["data"]):
                job_status = r["data"][0]["f_status"]
                print(f"toy test job {job_id} is {job_status}")
                if job_status in {"success", "failed", "canceled"}:
                    r = flow_client.job.log(job_id=job_id, output_path="./")
                    if r["retcode"] == 0:
                        log_msg = flow_client.test.check_toy(kwargs["guest_party_id"], job_status, r["directory"])
                        try:
                            for msg in log_msg:
                                print(msg)
                        except:
                            traceback.print_exc()
                    else:
                        print(f"get log failed, please check PROJECT_BASE/logs/{submit_result['jobId']}")
                    break
            time.sleep(1)
    else:
        prettify(submit_result)
