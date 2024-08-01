from objectbox import *


@Entity()
class TextChunk:
    # Unique identifier for the text chunk
    id = Id()

    # Name of the repository to which the chunk belongs
    repository_name = String()

    # Branch of the repository to which the chunk belongs
    repository_branch = String()

    # Name of the file to which the chunk belongs
    file_name = String()

    # Context (explication) of the chunk
    context = String()

    # Text content of the chunk
    text = String()

    # Path of the chunk within the file
    path = String()

    # Embedding of the chunk, used for vector searches
    embedding = Float32Vector(index=HnswIndex(
        dimensions=1536,
        distance_type=VectorDistanceType.COSINE
    ))


store = Store()
text_chunk = store.box(TextChunk)
