import os
import commit
import service

def go(squadron_dir, node_name, dry_run):
    result = commit.apply(squadron_dir, node_name, dry_run)

    if not dry_run:
        paths_changed = commit.commit(result)

        actions = {}
        reactions = []
        # Get all available actions and reactions
        for service_name in sorted(result):
            actions.update(service.get_service_actions(
                squadron_dir, service_name, result[service_name]['version']))
            reactions.extend(service.get_reactions(
                squadron_dir, service_name, result[service_name]['version']))

        service.react(actions, reactions, paths_changed)

