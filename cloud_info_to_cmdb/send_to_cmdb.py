#!/usr/bin/env python

import argparse
import json
import logging
import sys

import requests
import six


class SendToCMDB(object):
    def __init__(self, opts):
        self.opts = opts
        self.cmdb_read_url_base = opts.cmdb_read_endpoint
        self.cmdb_write_url = opts.cmdb_write_endpoint
        self.cmdb_auth = (opts.cmdb_user, opts.cmdb_password)
        self.sitename = opts.sitename
        self.delete_non_local_images = opts.delete_non_local_images
        self.debug = opts.debug
        self.verbose = opts.verbose
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
            logging.getLogger('requests').setLevel(logging.DEBUG)
            logging.getLogger('urllib3').setLevel(logging.DEBUG)
        elif self.verbose:
            logging.basicConfig(level=logging.INFO)
            logging.getLogger('requests').setLevel(logging.WARNING)
            logging.getLogger('urllib3').setLevel(logging.WARNING)

        self.service_id = None
        self.remote_images = {}
        self.local_images = {}

    def retrieve_service_id(self):
        url = "%s/service/filters/sitename/%s" % (self.cmdb_read_url_base,
                                                  self.sitename)
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            json_answer = r.json()
            logging.debug(json_answer)
            services = json_answer['rows']
            if len(services) > 1:
                logging.error("Multiple services found for %s" % self.sitename)
                sys.exit(1)
            else:
                self.service_id = json_answer['rows'][0]['id']
                logging.info("Service ID for %s is %s" %
                             (self.sitename, self.service_id))
        else:
            logging.error("Unable to retrieve service ID: %s" %
                          r.status_code)
            logging.error("Response %s" % r.text)
            sys.exit(1)

    def retrieve_remote_service_images(self, image_id):
        service_images = []
        # Find all images having the same name
        # TODO(gwarf) Ask for a way to use : or to search using local image_id
        # XXX filters/image_name does not allow to use name containing :
        # img_name = urllib.quote(image_name)
        # url = "%s/image/filters/image_name/%s" % (self.cmdb_read_url_base,
        #                                           img_name)
        # So lookup all of images of the service and check them all
        url = "%s/image/filters/service/%s" % (self.cmdb_read_url_base,
                                               self.service_id)
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            json_answer = r.json()
            logging.debug(json_answer)
            json_images = json_answer["rows"]
            if len(json_images) > 0:
                for img in json_images:
                    img_id = img['value']['image_id']
                    if img_id == image_id:
                        service_images.append(img)
                return service_images
            else:
                logging.debug("No images for image_id %s" % image_id)
        else:
            logging.error("Unable to query remote images: %s" %
                          r.status_code)
            logging.error("Response %s" % r.text)

    def retrieve_remote_image(self, cmdb_image_id):
        url = "%s/image/id/%s" % (self.cmdb_read_url_base, cmdb_image_id)
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            img_json_answer = r.json()
            logging.debug(img_json_answer)
            return img_json_answer
        else:
            logging.error("Unable to query remote image: %s" %
                          r.status_code)
            logging.error("Response %s" % r.text)

    def retrieve_remote_images(self):
        url = "%s/service/id/%s/has_many/images?include_docs=true" % (
              self.cmdb_read_url_base, self.service_id)
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            json_answer = r.json()
            logging.debug(json_answer)
            json_images = json_answer["rows"]
            logging.info("Found %s remote images" % len(json_images))
            if len(json_images) > 0:
                for image in json_images:
                    cmdb_image = {}
                    cmdb_image_id = image["id"]
                    cmdb_image_rev = image['doc']['_rev']
                    cloud_image_id = image['doc']['data']['image_id']
                    for key, val in image["doc"]["data"].iteritems():
                        cmdb_image[key] = val
                    cmdb_image['cmdb_image_id'] = cmdb_image_id
                    cmdb_image['cmdb_image_rev'] = cmdb_image_rev
                    logging.debug(cmdb_image)
                    self.remote_images[cloud_image_id] = cmdb_image
            else:
                logging.debug("No images for service %s" % self.service_id)
        else:
            logging.error("Unable to retrieve remote images: %s" %
                          r.status_code)
            logging.error("Response %s" % r.text)
            sys.exit(1)

    def retrieve_local_images(self):
        json_input = ''
        for line in sys.stdin.readlines():
            json_input += line.strip().rstrip('\n')
        # XXX we should exit cleanly if unable to parse stdin as JSON
        images = json.loads(json_input)
        for image in images:
            self.local_images[image['image_id']] = image
        logging.info("Found %s local images" % len(self.local_images))
        logging.debug(json_input)

    def _byteify(self, input):
        if isinstance(input, dict):
            return {self._byteify(key): self._byteify(value)
                    for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [self._byteify(element) for element in input]
        elif isinstance(input, six.text_type):
            return input.encode('utf-8')
        else:
            return input

    def submit_image(self, image):
        image_name = image["image_name"]
        image['service'] = self.service_id
        cmdb_image_id = None

        url = self.cmdb_write_url
        headers = {'Content-Type': 'application/json'}
        auth = self.cmdb_auth
        # XXX json.loads use unicode string
        # So convert unicode sting to byte strings
        # See http://stackoverflow.com/questions/956867
        data = '{"type":"image","data":%s}' % self._byteify(image)
        # XXX couchdb expect JSON to use double quotes
        data = data.replace("'", '"')
        logging.debug(data)
        r = requests.post(url, headers=headers, auth=auth, data=data)
        if r.status_code == requests.codes.created:
            logging.debug("Response %s" % r.text)
            json_answer = r.json()
            logging.debug(json_answer)
            cmdb_image_id = json_answer['id']
            image_rev = json_answer['rev']
            logging.info("Successfully imported image %s as %s rev %s" %
                         (image_name, cmdb_image_id, image_rev))
        else:
            logging.error("Unable to submit image: %s" % r.status_code)
            logging.error("Response %s" % r.text)

        return cmdb_image_id

    def purge_image_old_revisions(self, image, cmdb_image_id):
        image_name = image['image_name']
        image_id = image['image_id']
        # Find all images having the same id
        images = self.retrieve_remote_service_images(image_id)
        for img in images:
            cmdb_img_id = img['id']
            img_found = self.retrieve_remote_image(cmdb_img_id)
            rev = img_found['_rev']
            logging.debug("Found revision %s for image %s with id %s" %
                          (rev, image_name, cmdb_img_id))
            # keep latest image!
            if cmdb_img_id != cmdb_image_id:
                # delete old revision
                self.purge_image(image_name, cmdb_img_id, rev)

    def purge_image(self, image_name, cmdb_id, rev):
        url = "%s/%s?rev=%s" % (self.cmdb_write_url, cmdb_id, rev)
        logging.debug(url)
        headers = {'Content-Type': 'application/json'}
        auth = self.cmdb_auth
        r = requests.delete(url, headers=headers, auth=auth)
        if r.status_code == requests.codes.ok:
            logging.debug("Response %s" % r.text)
            logging.info("Deleted image %s, with id %s and rev %s" %
                         (image_name, cmdb_id, rev))
        else:
            logging.error("Unable to delete image: %s" % r.status_code)
            logging.error("Response %s" % r.text)

    def update_remote_images(self):
        # TODO(gwarf) store both kind of images using a common type/structure
        self.retrieve_local_images()
        self.retrieve_remote_images()

        images_to_delete = []
        images_to_update = []
        images_to_add = []

        for image_id, image in self.local_images.items():
            if image['image_id'] not in self.remote_images.keys():
                images_to_add.append(image)
            else:
                images_to_update.append(image)

        for image_id, image in self.remote_images.items():
            if image['image_id'] not in self.local_images.keys():
                images_to_delete.append(image)

        logging.info("Images to import: %s" % len(images_to_add))
        logging.info("Images to update: %s" % len(images_to_update))
        logging.info("Images to delete: %s" % len(images_to_delete))

        for image in images_to_add:
            self.submit_image(image)

        for image in images_to_update:
            # XXX check if update/PUT might be preferable
            cmdb_image_id = self.submit_image(image)
            if cmdb_image_id:
                self.purge_image_old_revisions(image, cmdb_image_id)

        if self.delete_non_local_images:
            for image in images_to_delete:
                image_name = image['image_name']
                cmdb_image_id = image['cmdb_image_id']
                cmdb_image_rev = image['cmdb_image_rev']
                self.purge_image(image_name, cmdb_image_id, cmdb_image_rev)


def parse_opts():
    parser = argparse.ArgumentParser(
        description='Submit images to CMDB',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        fromfile_prefix_chars='@',
        conflict_handler="resolve",
    )

    parser.add_argument(
        '--cmdb-read-endpoint',
        default='http://indigo.cloud.plgrid.pl/cmdb',
        help=('URL of the CMDB endpoint'))

    parser.add_argument(
        '--cmdb-write-endpoint',
        default='http://couch.cloud.plgrid.pl/indigo-cmdb-v2',
        help=('URL of the CMDB endpoint'))

    parser.add_argument(
        '--cmdb-user',
        required=True,
        help=('Username to use to contact the CMDB endpoint'))

    parser.add_argument(
        '--cmdb-password',
        required=True,
        help=('Password to use to contact the CMDB endpoint'))

    parser.add_argument(
        '--sitename',
        required=True,
        help=('CMDB target site name'
              'Images will be linked to the corresponding service ID'))

    parser.add_argument(
        '--delete-non-local-images',
        action='store_true',
        help=('Delete images that are not present locally'))

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help=('Verbose output'))

    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help=('Debug output'))

    return parser.parse_args()


def main():
    opts = parse_opts()

    sender = SendToCMDB(opts)
    sender.retrieve_service_id()
    sender.update_remote_images()


if __name__ == '__main__':
    main()
