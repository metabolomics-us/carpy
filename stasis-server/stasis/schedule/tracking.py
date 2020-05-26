import os
import re


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
                print("content:")
                print(f"task: {m.group(2)}")
                print(detail)
                print(overrides)
                print("")
            else:
                print(f"rejected => wrong env!. event belongs to {m.group(1)}, but we require it to be {os.getenv('current_stage')}")
        else:
            print(f"invalid group specified, which doesn't match the pattern. Group was {group} and patter was {pattern}")

    except Exception as e:
        print(f"something failed: {e}")
        print(event)
        print(context)
