function singplural(what, length) {
  if (length === 1) {
    return what
  }

  return `${what}s`
}