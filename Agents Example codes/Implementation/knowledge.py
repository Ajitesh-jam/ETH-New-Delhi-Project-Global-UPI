from hyperon import MeTTa, E, S, ValueAtom # This is in python3.12

def initialize_financial_knowledge_graph(metta: MeTTa):
    """
    Populates the MeTTa space with the structural knowledge of valid
    conversion paths and their associated costs.
    Rates are no longer stored here; they will be added dynamically.
    """
    metta.space().add_atom(E(S("path"), S("INR"), S("USD"), S("ETH"), ValueAtom(0.001)))
    metta.space().add_atom(E(S("path"), S("INR"), S("USD"), S("MATIC"), ValueAtom(0.0008)))
    
    # For Adding more cryptos , we just add them in this relationship graph