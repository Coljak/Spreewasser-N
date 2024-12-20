#!/usr/bin/python
# -*- coding: UTF-8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */

# Authors:
# Michael Berg-Mohnicke <michael.berg@zalf.de>
#
# Maintainers:
# Currently maintained by the authors.
#
# This file has been created at the Institute of
# Landscape Systems Analysis at the ZALF.
# Copyright (C: Leibniz Centre for Agricultural Landscape Research (ZALF)

import os
import zmq

def run_consumer(path_to_output_dir = None, leave_after_finished_run = True, server = {"server": None, "port": None}, shared_id = None):
    "collect data from workers"

    config = {
        "port": "7777",
        "server": "swn_monica", 
        "shared_id": shared_id,
        "out": path_to_output_dir if path_to_output_dir else os.path.join(os.path.dirname(__file__), 'monica_output/'),
        "leave_after_finished_run": leave_after_finished_run
    }

    # print("consumer config:", config)

    context = zmq.Context()
    if config["shared_id"]:
        socket = context.socket(zmq.DEALER)
        socket.setsockopt(zmq.IDENTITY, config["shared_id"])
        print("Consumer shared_id: ", config["shared_id"])
    else:
        socket = context.socket(zmq.PULL)
    socket.connect("tcp://" + config["server"] + ":" + config["port"])

    #socket.RCVTIMEO = 1000
    leave = False

    def process_message(msg):

        if not hasattr(process_message, "wnof_count"):
            process_message.received_env_count = 0

        leave = False

        if msg["type"] == "finish":
            print("c: received finish message")
            leave = True

        else:
            print("c: received work result ", process_message.received_env_count, " customId: ", str(msg.get("customId", "")))

            process_message.received_env_count += 1

            # check if message has errors
            if msg.get("errors", []):
                print("c: received errors: ", msg["errors"])

            # print('msg', msg["data"], "Type: ", type(msg))
                for k, v in msg.items():
                    print("key", k, "value: ", v)
           
            
            if config["leave_after_finished_run"] == True :
                leave = True

        # return leave
        print("leaving process", leave)
        return leave

    while not leave:
        try:
            msg = socket.recv_json()
            leave = process_message(msg)
        except:
            continue

    print("c: exiting run_consumer()")
    return msg
    #debug_file.close()

if __name__ == "__main__":
    run_consumer()
    