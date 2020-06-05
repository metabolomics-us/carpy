import os
import re

from stasis.tables import insert_ecs_event


def ecs(event, context):
    try:
        detail = event['detail']
        group = detail['group']

        pattern = re.compile("^family:([a-zA-Z]+)-(.*)")

        if pattern.match(group):
            print("stage: {}".format(os.getenv("current_stage")))

            m = pattern.search(group)

            if m.group(1) == os.getenv("current_stage"):
                print("task belong to our environment")

                overrides = detail['overrides']
                container = detail['containers'][0]
                print("content:")
                print(f"task: {m.group(2)}")
                print(detail)
                print(overrides)
                print("")

                id = event['id']
                task = m.group(2)
                cpu = detail['cpu']
                memory = detail['memory']
                status = detail['lastStatus']
                image = container['image']
                digest = container['imageDigest']
                exitCode = container['exitCode']
                startedAt = detail['startedAt']
                stoppedAt = detail['stoppedAt']
                stopReason = detail['stoppedReason']

                insert = {
                    'id': id,
                    'task': task,
                    'taskDefinition': detail['taskDefinitionArn'],
                    'cpu': int(cpu),
                    'memory': int(memory),
                    'status': status,
                    'image': image,
                    'digest': digest,
                    'exitCode': exitCode,
                    'startedAt': startedAt,
                    'stoppedAt': stoppedAt,
                    'stopReason': stopReason,
                    'env': overrides['containerOverrides'][0]['environment']
                }

                # store in the database now
                insert_ecs_event(insert)
                pass
            else:
                print(
                    f"rejected => wrong env!. event belongs to {m.group(1)}, but we require it to be {os.getenv('current_stage')}")
        else:
            print(
                f"invalid group specified, which doesn't match the pattern. Group was {group} and patter was {pattern}")

    except Exception as e:
        print(f"something failed: {e}")
        print(context)
        raise e
