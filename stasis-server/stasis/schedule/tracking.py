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

            if m.group(0) == os.getenv("current_stage"):
                print("task belong to our environment")

                print("content:")
                print(f"task: {m.group(1)}")
                print(group)
                print(detail)
                print(event)
                print("")
            else:
                print("rejected => wrong env!")
        else:
            print(f"invalid group specified, which doesn't match the pattern. Group was {group} and patter was {pattern}")

        print(event)
    except Exception as e:
        print(f"something failed: {e}")
        print(event)
        print(context)
