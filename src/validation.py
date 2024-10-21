from resources.validation.sample_validation import Ingestion_validation
def raw_files_validation():
    var_branch_validation=Ingestion_validation().validation_execute()
    return var_branch_validation

def branch_check(**kwargs):
    ti = kwargs['ti']
    var_branch_validation = ti.xcom_pull(task_ids='brew_ingestion_validation')

    if var_branch_validation  != 0:
        return 'simulated_action'
    return 'bronze_to_silver'


def simulated_branch():
    print("This is the simulated task that in case the branch check returns false, will be executed.")
    print("Examples here will be like a try flux or msg direct to the ingestion team chat")
