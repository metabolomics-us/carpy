def test_initial_dict_to_panda(cis_cli,my_AnnotationReader,splash_test_name_with_members):
    '''
    First, get a result from the client
    Then, put that result into the AnnotationReader 
    '''
    temp_annotation_result=cis_cli.get_annotations_given_splash(splash_test_name_with_members[0])
    my_AnnotationReader.initial_dict_to_panda(temp_annotation_result)

    errors=list()

    #if there are any nan
    if my_AnnotationReader.panda_representation.isnull().values.any():
        errors.append('at least one nan found')
    #i can put additional, meaningful errors here

    assert not errors, "errors occured:\n{}".format("\n".join(errors))