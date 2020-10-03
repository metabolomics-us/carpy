SERVICE = "stasis-service"
MESSAGE_BUFFER = 10
SECURE_CARROT_RUNNER = 'secure-carrot-runner'
SECURE_CARROT_AGGREGATOR = 'secure-carrot-aggregator'
SECURE_CARROT_STEAC = 'secure-carrot-steac'

##
# these are tasks which can run in paralell
MAX_FARGATE_TASKS_BY_SERVICE = {
    SECURE_CARROT_RUNNER: 40,
    SECURE_CARROT_AGGREGATOR: 2
}

##
# these are tasks which need to be exclusive
SINGULAR_FARGATE_SERVICES = [
    SECURE_CARROT_STEAC
]

##
# computes the maxinum number of tasks to be run
MAX_FARGATE_TASKS = sum(MAX_FARGATE_TASKS_BY_SERVICE.values())

##
# do we permit automatic scheduling using cloud resources
#
ENABLE_AUTOMATIC_SCHEDULING = False
