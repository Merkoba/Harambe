let clicked = false

window.onload = () => {
  let captcha = document.querySelector(`#captcha-text`)

  if (captcha) {
    captcha.placeholder = `Enter the captcha`
  }

  let image = document.querySelector(`#image`)

  if (image) {
    image.addEventListener(`click`, (e) => {
      window.scrollTo(0, document.body.scrollHeight)
    })

    image.addEventListener(`auxclick`, (e) => {
      if (e.button === 1) {
        window.location = `/admin`
      }
    })
  }

  document.addEventListener(`dragover`, (e) => {
    e.preventDefault()
  })

  document.addEventListener(`drop`, (e) => {
    e.preventDefault()
    let files = e.dataTransfer.files

    if (files && (files.length > 0)) {
      let file = document.querySelector(`#file`)
      let dataTransfer = new DataTransfer()
      dataTransfer.items.add(files[0])
      file.files = dataTransfer.files
    }
  })
}

function validate() {
  if (clicked) {
    return false
  }

  let captcha = document.querySelector(`#captcha-text`)

  if (captcha) {
    if (!captcha.value.trim()) {
      return false
    }
  }

  let key = document.querySelector(`#key`)

  if (key) {
    if (!key.value.trim()) {
      return false
    }
  }

  let file = document.querySelector(`#file`)
  let file_length = file.files.length

  if (file_length === 0) {
    return false
  }

  if (file_length > 1) {
    return false
  }

  if (file.files[0].size > max_size) {
    return false
  }

  clicked = true
  return true
}