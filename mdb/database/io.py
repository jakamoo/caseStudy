from threading import Lock
import os
import json
from git import Repo

mutex = Lock()


def __add_helper(mdb, data):
    """ Private Helper Function.
    Go through target path and creates new data type
    :param data: incoming json file.
    :param sha_list: sha list of all attribute such as context
    :return: none
    """





    datatype = data["datatype"]
    dir_datatype = os.path.join(mdb.get_basedir(), datatype)

    if os.path.exists(dir_datatype):

        # update static log to update log.txt
        with open(os.path.join(mdb.get_basedir(), datatype, "index")) as json_file:
            total = json.load(json_file)

        filename = "file" + str(len(total) + 1) + ".txt"

        sha_dic = {}

        for attribute in mdb.get_attributes():

            dir_attribute = os.path.join(mdb.get_basedir(), datatype, attribute)
            file_path = os.path.join(dir_attribute, filename)

            if os.path.exists(dir_attribute):

                # create new file and add to repo
                with open(file_path, 'w') as outfile:
                    json.dump(data[attribute], outfile)

                # git add
                mdb.git_add(dir_attribute, filename, data["commit"])

                sha_dic[attribute] = mdb.get_first_sha(dir_attribute, filename)
                # --------------------------------

        # add new dictionary to index list
        total.append(sha_dic)

        #                  #
        # index operations #
        #                  #
        with open(os.path.join(mdb.get_basedir(), datatype, "index"), 'w') as outfile:
            json.dump(total, outfile)

        # git add
        mdb.git_add(dir_datatype, "index", data["commit"])

        # return index sha key
        return mdb.get_last_sha(os.path.join(mdb.get_basedir(), datatype), "index")

    else:
        pass


def add_instance(mdb, data):
    """
    It is dependent to name of data type.
    if new data type required to add new file structure is created.
    Otherwise, add just a new file.

    input example;
        r = {
            "datatype": "graph",   # may be polynomial
            "raw": "raw example",
            "features": "features example",
            "semantics": "semantics example",
            "context":  {"edge": {"1": 100, "2": 2000},
                         "vertex": [{"first": 4, "second": 4},
                                    {"first": 3, "second": 55}]},
            "typeset": "typeset example",
            "commit": "update_repo"
        }
    return example;

        {sha : a63813d76910623f2b92ca7343682fe9ee2230a1 , 'status': 1}
        if removal is unsuccessful;
        {'status': 0} # this line will be rewrite

    :param data: incoming json file.
    :return: sha key of index of datatype.
    """
    '''
    mutex.acquire()
    try:
        index_sha = __add_helper(mdb, data)
    finally:
        mutex.release()

    status = 1  # will be fix
    response = {
        "sha": index_sha,    # index represent all of datatype to perform on it.
        "status": status                            # if successful otherwise 0
    }
    '''

    response = {
        "sha": "84354c98e8198a0554252a3124dab8e3ae8cf90b"
    }

    return response


def remove_instance(mdb, data):
    """
    It is dependent to name of data type and its sha key.
    An example as fallow;

    input example;

        r = {
            "datatype": "graph",
            "sha": "a9f870b98077b86f4cff2afbb90c3255c8f9a923"
        }

        other example

        r = {
            "datatype": "polynomial",
            "sha": "12b8a0b98077b86f4cff2afbb90c3255c8f9affc"
        }

    return example;

        {'status': 1}

        if removal is unsuccessful;

        {'status': 0}

    :param data: incoming json file.
    :return: control status
    """
    status = 0
    datatype = data["datatype"]

    if os.path.exists(datatype):

        input_sha = data["sha"]

        dir_index = os.path.join(mdb.get_basedir(), datatype, "index")

        for filename in os.listdir(dir_index):

            # we ignore .git file
            if filename == ".git":
                continue

            if input_sha == mdb.get_first_sha(dir_index, filename):

                for attribute in mdb.get_attributes():

                    path = os.path.join(mdb.get_basedir(), datatype, attribute)

                    mdb.git_remove(path, filename, "deleted repo")

                status = 1

                # decrease log file data type and write to log again
                mdb.get_file_number()["remaining-" + datatype] -= 1
                with open(os.path.join(mdb.get_basedir(), "log.txt"), 'w') as outfile:
                    json.dump(mdb.get_file_number(), outfile)

                break

    response = {
        "status": status  # if successful otherwise 0
    }

    return response


def retrieve_instance(mdb, data):

    """ Fetches an instance which match with "input" sha key

    input example;

        r = {
            "datatype": "graph",
            "sha": "18e8b2047eeefe9d45fa01a2f15b26bb62a3c471"
        }

        other example

        r = {
            "datatype": "polynomial",
            "sha": "21fa767a68101f4b7e75ffe50001954d0ee37a74"
        }

    return example;

        r = {
            "datatype": "graph",   # may be polynomial
            "raw": "raw example",
            "features": "features example",
            "semantics": "semantics example",
            "context":  {"edge": {"1": 100, "2": 2000},
                         "vertex": [{"first": 4, "second": 4},
                                    {"first": 3, "second": 55}]},
            "typeset": "typeset example"
        }

    :param data: incoming json file.
    :return: desired instance
    """

    datatype = data["datatype"]

    response = {"datatype": datatype}

    status = -1

    if not os.path.exists(datatype):
        status = 0

    else:
        input_sha = data["sha"]

        dir_index = os.path.join(mdb.get_basedir(), datatype, "index")

        for filename in os.listdir(dir_index):

            if filename == ".git":
                continue

            if input_sha == mdb.get_first_sha(dir_index, filename):
                for attribute in mdb.get_attributes():
                    file_path = os.path.join(mdb.get_basedir(), datatype, attribute, filename)

                    with open(file_path, "r") as json_file:
                        response[attribute] = json.load(json_file)

                status = 1
                break

    response["status"] = status

    return response


def __update_file(mdb, content, path, commit_message, filename):

    """Private Helper Function.
    Write new data to target file. Add repository with new commit message
    :param content: New content to edit target file
    :param path: repository path
    :param commit_message:
    :param filename:
    :return: none
    """


    # generate path
    file_path = os.path.join(path, filename)

    # write target file
    with open(file_path, 'w') as outfile:
        json.dump(content, outfile)

    mdb.git_add(path, filename, commit_message)

    
    
def update_instance(mdb, data):
    """
    update instance which match with "input" sha key

    input example;

        r = {
            "datatype": "graph",   # may be polynomial
            "sha": "12b8a0b98077b86f4cff2afbb90c3255c8f9affc",
            "index": "index example",
            "raw": "raw example",
            "features": "features example",
            "semantics": "semantics example",
            "context":  {"edge": {"1": 100, "2": 2000},
                         "vertex": [{"first": 4, "second": 4},
                                    {"first": 3, "second": 55}]},
            "typeset": "typeset example",
            "commit": "update_repo"
        }


    return example;

        {'status': 1}

        if removal is unsuccessful;

        {'status': 0}

    :param data: incoming json file.
    :return:
    """

    datatype = data["datatype"]

    status = 0

    if not os.path.exists(datatype):
        status = 0

    else:
        input_sha = data["sha"]

        dir_index = os.path.join(mdb.get_basedir(), datatype, "index")

        for filename in os.listdir(dir_index):

            if filename == ".git":
                continue

            if input_sha == mdb.get_first_sha(dir_index, filename):
                for attribute in mdb.get_attributes():
                    dir_attribute = os.path.join(mdb.get_basedir(), datatype, attribute)

                    __update_file(mdb, data[attribute], dir_attribute, data["commit"], filename)
                status = 1
                break

    response = {
        "status": status  # if successful otherwise 0
    }

    return response

