App.get_storage = () => {
  let storage = localStorage.getItem(App.ls_storage)
  let obj

  if (storage) {
    obj = JSON.parse(storage)
  }
  else {
    obj = {}
  }

  App.storage = obj
}

App.save_storage = () => {
  localStorage.setItem(App.ls_storage, JSON.stringify(App.storage))
}

App.storage_value = (what, fallback) => {
  let value = App.storage[what]

  if (value === undefined) {
    return fallback
  }

  return value
}