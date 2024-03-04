from hyperon_das import DistributedAtomSpace

distributed_atom_space = DistributedAtomSpace(
    query_engine="remote",
    host="localhost",
    port=8080,
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
