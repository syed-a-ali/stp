stp = {
    'accounts': {
        'dev-pangea': {
            'param_store_name': '/dev/stp/key',
            'env': 'demo'
        },
        'dev-stp': {
            'param_store_name': '/dev/stp/key-demo-data',
            'env': 'demo'
        },
        'prod': {
            'param_store_name': '/prod/stp/key',
            'env': 'prod'
        }
    }
}

aws = {
    'bucket_name': 'pangea-data-lake-west',
    'prefix': 'partner/stp/'
}
