from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import boto3
import json
import datetime
import config
import requests


def get_params(parameter_name, region='us-west-2'):
    ssm = boto3.client('ssm', region_name=region)
    response = ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )
    return json.loads(response['Parameter']['Value'])


def get_string_to_sign(empresa, fecha_operacion=""):
    return f"|||{empresa}|{fecha_operacion}|||||||||||||||||||||||||||||||||"


def get_signature(company, keystore, password, fecha_operacion):
    string_to_encode = get_string_to_sign(company, fecha_operacion.strftime('%Y%m%d'))

    with open(keystore, 'rb') as f:
        key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            f.read(),
            str.encode(password))

    signed_string = key.sign(
        str.encode(string_to_encode),
        padding.PKCS1v15(),
        hashes.SHA256())

    return base64.b64encode(signed_string)


def get_stp_config(account_name):
    param_store_name = config.stp['accounts'][account_name]['param_store_name']
    env = config.stp['accounts'][account_name]['env']
    return env, param_store_name


def call_stp(url, body, env='prod'):
    verify = True if env == 'prod' else False
    response = requests.post(url, json=body, verify=verify)
    return response.content


def write_data(data, env, endpoint, fecha_operacion):
    directory = config.aws['prefix'] + env + '/' + endpoint
    filename = fecha_operacion.strftime('%Y%m%d') + '.json'
    s3 = boto3.client('s3')
    response = s3.put_object(
        Bucket=config.aws['bucket_name'],
        Body=data,
        Key=directory + '/' + filename
    )
    print(response)


is_historical = True
fecha_operacion = datetime.datetime(2021, 3, 2)
estado = 'R'
account = 'dev-pangea'
endpoint = 'ordenPago/consOrdenesFech'
env, param_store_name = get_stp_config(account)
params = get_params(param_store_name)
empresa = params['Company']
firma = get_signature(empresa, params['Keystore'], params['Password'], fecha_operacion)

body = dict(
    estado=estado,
    empresa=empresa,
    firma=firma.decode()
)

if is_historical:
    body['fechaOperacion'] = int(fecha_operacion.strftime('%Y%m%d'))

data = call_stp(params['EndpointUrl'] + endpoint, body, env)
write_data(data, env, endpoint, fecha_operacion)
