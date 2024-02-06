from hyperon_das import DistributedAtomSpace

distributed_atom_space = DistributedAtomSpace(
    atomdb="redis_mongo",
    mongo_hostname="localhost",
    mongo_port=27017,
    mongo_username="admin",
    mongo_password="admin",
    redis_hostname="localhost",
    redis_port=6379,
    redis_ssl=False,
    redis_cluster=False,
)

print(distributed_atom_space.count_atoms())

print(
    distributed_atom_space.query(
        {
            "atom_type": "link",
            "type": "Similarity",
            "targets": [
                {"atom_type": "node", "type": "Concept", "name": "human"},
                {"atom_type": "node", "type": "Concept", "name": "monkey"},
            ],
        }
    )
)
