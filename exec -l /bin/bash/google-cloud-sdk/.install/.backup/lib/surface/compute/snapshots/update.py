# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command for labels update to snapshots."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.operations import poller
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.snapshots import flags as snapshots_flags
from googlecloudsdk.command_lib.util import labels_util


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Update(base.UpdateCommand):
  r"""Update a Google Compute Engine snapshot.

  *{command}* updates labels for a Google Compute snapshot.
  For example:

    $ {command} example-snapshot \
      --update-labels=k0=value1,k1=value2 --remove-labels=k3

  will add/update labels ``k0'' and ``k1'' and remove labels with key ``k3''.

  Labels can be used to identify the snapshot and to filter them as in

    $ {parent_command} list --filter='labels.k1:value2'

  To list existing labels

    $ {parent_command} describe example-snapshot --format='default(labels)'

  """

  @staticmethod
  def Args(parser):
    Update.SnapshotArg = snapshots_flags.MakeSnapshotArg()
    Update.SnapshotArg.AddArgument(parser)
    labels_util.AddUpdateLabelsFlags(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client.apitools_client
    messages = holder.client.messages

    snapshot_ref = Update.SnapshotArg.ResolveAsResource(
        args, holder.resources)

    update_labels, remove_labels = labels_util.GetAndValidateOpsFromArgs(args)

    snapshot = client.snapshots.Get(
        messages.ComputeSnapshotsGetRequest(**snapshot_ref.AsDict()))

    replacement = labels_util.UpdateLabels(
        snapshot.labels,
        messages.GlobalSetLabelsRequest.LabelsValue,
        update_labels=update_labels,
        remove_labels=remove_labels)

    if not replacement:
      return snapshot

    request = messages.ComputeSnapshotsSetLabelsRequest(
        project=snapshot_ref.project,
        resource=snapshot_ref.snapshot,
        globalSetLabelsRequest=
        messages.GlobalSetLabelsRequest(
            labelFingerprint=snapshot.labelFingerprint,
            labels=replacement))

    operation = client.snapshots.SetLabels(request)
    operation_ref = holder.resources.Parse(
        operation.selfLink, collection='compute.globalOperations')

    operation_poller = poller.Poller(client.snapshots)
    return waiter.WaitFor(
        operation_poller, operation_ref,
        'Updating labels of snapshot [{0}]'.format(
            snapshot_ref.Name()))
