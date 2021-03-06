#!/usr/bin/env python
import argparse
import base64
import json
import os
import errno


from pprint import pprint

def read_certificate(json_cert):
    return base64.b64decode(json_cert)

# def read_privatekey(json_cert):
#     return base64.b64decode(json_cert)

def read_cert(storage_dir, filename):
    cert_path = os.path.join(storage_dir, filename)
    if os.path.exists(cert_path):
        with open(cert_path) as cert_file:
            return cert_file.read()
    return None

def read_certs(acme_json_path):
    with open(acme_json_path) as acme_json_file:
        acme_json = json.load(acme_json_file)

        certs_json = acme_json['Certificates']
        certs = {}
        for cert in certs_json:
            domain = cert['Domain']['Main']
            # domain_cert = cert['Certificate']
            # domain_key = cert['Key']
            # Only get the first cert (should be the most recent)
            if domain not in certs:
                certs[domain] = dict()
                certs[domain]['Certificate'] = read_certificate(cert['Certificate'])
                certs[domain]['PrivateKey'] = read_certificate(cert['Key'])

    return certs

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def write_cert(storage_dir, domain, cert_content, filename):
    cert_dir = os.path.join(storage_dir,domain)
    make_sure_path_exists(cert_dir)
    cert_path = os.path.join(cert_dir, '%s.pem' % (filename))
    with open(cert_path, 'wb') as cert_file:
        cert_file.write(cert_content)
    os.chmod(cert_path, 0o600)


def main():
    parser = argparse.ArgumentParser(
        description="Dump all certificates out of Traefik's acme.json file")
    parser.add_argument('acme_json', help='path to the acme.json file')
    parser.add_argument('dest_dir',
                        help='path to the directory to store the certificate')

    args = parser.parse_args()

    certs = read_certs(args.acme_json)

    # pprint( certs )

    print('Found certs for %d domains' % (len(certs),))
    for domain, cert in certs.items():
        print('Writing cert for domain %s' % (domain,))
        write_cert(args.dest_dir, domain, cert['Certificate'], 'fullchain')
        write_cert(args.dest_dir, domain, cert['PrivateKey'], 'privkey')


    print('Done')

if __name__ == '__main__':
    main()
