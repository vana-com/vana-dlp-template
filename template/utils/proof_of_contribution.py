import json
import os
import tempfile
import zipfile

import requests
import vana

import template.protocol
from template.models.user import User
from template.utils.config import get_validation_config


async def proof_of_contribution(message: template.protocol.ValidationMessage) -> template.protocol.ValidationMessage:
    local_zip_path = download_file(message.input_file_url)

    if local_zip_path is None:
        message.output_file_is_valid = False
        message.output_file_score = 0
    else:
        is_valid, file_score = proof_of_quality(local_zip_path).values()
        message.output_file_is_valid = is_valid
        message.output_file_score = file_score

        proof_of_ownership(local_zip_path)
        proof_of_uniqueness(local_zip_path)

        # Clean up
        os.remove(local_zip_path)
        vana.logging.info(f"Data removed from the node")

    return message


def download_file(input_url) -> str | None:
    """
    Download a file from a URL.
    :param input_url:
    :return: Local file path
    """
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "data.zip")
    response = requests.get(input_url)

    if response.status_code != 200:
        vana.logging.error(f"Failed to download file from {input_url}")
        return None
    else:
        with open(file_path, 'wb') as f:
            f.write(response.content)

    return file_path


def proof_of_quality(zip_file_path):
    """
    Check the quality of a zip file
    :param zip_file_path: Path to the zip file
    :return: Object containing a quality score and whether the file is valid
    """
    required_files = ['user.json']
    user_data: User | None = None

    # Load data from zip file and validate that it contains the required files
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        file_names = zip_ref.namelist()
        if not all(file in file_names for file in required_files):
            raise ValueError(f"Zip file does not contain all required files: {required_files}")

        with zip_ref.open('user.json') as file:
            user_data_json = json.load(file)
            user_data = User(**user_data_json)

    validation_config = get_validation_config()
    user_reputation = user_data.reputation if user_data is not None else 0

    return {
        'is_valid': user_reputation > validation_config["MIN_REPUTATION"],
        'file_score': user_reputation
    }


def proof_of_ownership(local_file_path):
    """
    Check the ownership of the file.
    :param local_file_path:
    :return:
    """
    # TODO: Implement ownership check proving that the zip file is owned by the user that submitted it
    pass


def proof_of_uniqueness(local_file_path):
    """
    Check the similarity of the file with previously validated files.
    :param local_file_path:
    :return:
    """
    # TODO: Implement a similarity check to ensure the file is not a
    #  duplicate (or near duplicate) of a previously submitted file
    pass
