import os
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from template.protocol import ValidationMessage
from template.utils.proof_of_contribution import proof_of_contribution


@pytest.fixture
def file_zip():
    return os.path.join(os.getcwd(), 'tests/data/template_data.zip')


@pytest.mark.asyncio
async def test_proof_of_contribution(mocker: MonkeyPatch, file_zip: str) -> None:
    # Mock the decryption function and return our mocked file
    mock_download: Mock = mocker.patch('template.utils.proof_of_contribution.download_file')
    mock_download.return_value = file_zip
    mock_os: Mock = mocker.patch('template.utils.proof_of_contribution.os.remove')

    validation_message: ValidationMessage = await proof_of_contribution(ValidationMessage(input_file_url='url'))

    assert validation_message.output_file_is_valid is True
    assert validation_message.output_file_score > 0.5
    mock_download.assert_called()
    mock_os.assert_called()
