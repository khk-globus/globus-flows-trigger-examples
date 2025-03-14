#!/usr/bin/env python

import argparse
import os

# This could go into a different file and be invoked without the file watcher
from flows_service import create_flows_client


def run_flow(event_file):

    # TODO: Specify the flow to run when triggered
    flow_id = "REPLACE_WTIH_FLOW_ID"
    fc = create_flows_client(flow_id=flow_id)

    # TODO: Set a label for the flow run
    # Default includes the file name that triggered the run
    flow_label = f"Trigger tar->transfer: {os.path.basename(event_file)}"

    # TODO: Modify list of tar inputs
    # May contain files or directories
    tar_inputs = [
        "/add/to/archive/path1",
        "/add/to/archive/path2",
        "/add/to/archive/pathN",
    ]

    # TODO: Modify tar filename
    tar_output = "/path/to/archive/file.tgz"

    # TODO: Modify Globus Compute endpoint ID where tar will run
    # The Globus Compute agent must be installed on a system that
    # has access to the source collection containing the tar inputs
    compute_endpoint_id = "REPLACE_WITH_COMPUTE_ENDPOINT_ID"

    # TODO: Specify the tar function id
    # The tar function is defined in tar_function.py, and must be registered
    # with the Globus Compute service.
    compute_function_id = "REPLACE_WITH_REGISTERED_FUNCTION_ID"

    # TODO: Modify source collection ID
    # Source collection must be on the endpoint where this trigger code is running
    source_id = "REPLACE_WITH_SOURCE_COLLECTION_ID"

    # TODO: Modify destination collection ID
    destination_id = "REPLACE_WITH_DESTINATION_COLLECTION_ID"

    # TODO: Modify destination collection path
    # Update path to include your user name e.g. /automate-tutorial/dev1/
    destination_base_path = "/home/ubuntu/"

    # Get the directory where the triggering file is stored and
    # add trailing '/' to satisfy Transfer requirements for moving a directory
    event_folder = os.path.dirname(event_file)

    # Get name of monitored folder to use as destination path
    # and for setting permissions
    event_folder_name = os.path.basename(event_folder)
    destination_path = os.path.join(destination_base_path, os.path.basename(tar_output))

    # Inputs to the flow
    flow_input = {
        "tar": {
            "compute_endpoint_id": compute_endpoint_id,
            "compute_function_id": compute_function_id,
            "compute_function_kwargs": {"inputs": tar_inputs, "output": tar_output},
        },
        "transfer": {
            "source_collection": source_id,
            "source_path": tar_output,
            "destination_collection": destination_id,
            "destination_path": destination_path,
        },
    }

    flow_run_request = fc.run_flow(
        body=flow_input,
        label=flow_label,
        tags=["Trigger_Tutorial"],
    )
    print(f"Transferring: {event_folder_name}")
    print(f"https://app.globus.org/runs/{flow_run_request['run_id']}")


# Parse input arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        Watch a directory and trigger a simple transfer flow."""
    )
    parser.add_argument(
        "--watchdir",
        type=str,
        default=os.path.abspath("."),
        help=f"Directory path to watch. [default: current directory]",
    )
    parser.add_argument(
        "--patterns",
        type=str,
        default="",
        nargs="*",
        help='Filename suffix pattern(s) that will trigger the flow. [default: ""]',
    )
    parser.set_defaults(verbose=True)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Creates and starts the watcher
    from watch import FileTrigger

    trigger = FileTrigger(
        watch_dir=os.path.expanduser(args.watchdir),
        patterns=args.patterns,
        FlowRunner=run_flow,
    )
    trigger.run()
