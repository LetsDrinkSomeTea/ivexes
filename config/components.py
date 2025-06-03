def banner(model: str, temperature: float, max_turns: int) -> str:
    return r"""
    o-O-o o   o o--o     o--o  o-o  
      |   |   | |        |    |     
      |   o   o O-o  \ / O-o   o-o  
      |    \ /  |     o  |        | 
    o-O-o   o   o--o / \ o--o o--o  
    
    Intelligent Vulnerability Extraction
           & Exploit Synthesis
    """ + f"""
    model:       {model}
    temperature: {temperature}
    max turns:   {max_turns}
    """

