import re
from markdown import Markdown
from markdown.extensions.extra import ExtraExtension
from markdown.preprocessors import Preprocessor
from errbot.rendering.ansiext import AnsiExtension, enable_format, IMTEXT_CHRS

MARKDOWN_LINK_REGEX = re.compile(r'(?<!!)\[(?P<text>[^\]]+?)\]\((?P<uri>[a-zA-Z0-9]+?:\S+?)\)')

def hangoutschat_markdown_converter(compact_output=False):
    """
    This is a Markdown converter for use with HangoutsChat.
    """
    enable_format('imtext', IMTEXT_CHRS, borders=not compact_output)
    md = Markdown(output_format='imtext', extensions=[ExtraExtension(), AnsiExtension()])
    md.preprocessors['LinkPreProcessor'] = LinkPreProcessor(md)
    md.stripTopLevelTags = False
    return md


class LinkPreProcessor(Preprocessor):
    """
    This preprocessor converts markdown URL notation into Hangouts Chat URL notation
    as described at https://developers.google.com/hangouts/chat/reference/message-formats/basic, section "Linking to URLs".
    """
    def run(self, lines):
        for i, line in enumerate(lines):
            lines[i] = MARKDOWN_LINK_REGEX.sub(r'&lt;\2|\1&gt;', line)
        return lines