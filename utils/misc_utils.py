def find_and_replace(text_widget, find_text, replace_text):
    content = text_widget.get("1.0", "end")
    new_content = content.replace(find_text, replace_text)
    text_widget.delete("1.0", "end")
    text_widget.insert("end", new_content)
