App.init = () => {
  App.date_ms = App.post.date * 1000
  App.refresh_count = 0
  App.max_on = false
  App.max_id = ``
  App.image_expanded = false
  App.modal_image_container_id = `#Msg-content-container-modal_image`
  App.modal_image_scroll_step = 80
  App.editor_lines = 25

  let edit = DOM.el(`#edit`)

  if (edit) {
    App.setup_edit_post_opts()

    DOM.ev(edit, `click`, () => {
      App.edit_post()
    })

    DOM.ev(edit, `auxclick`, (e) => {
      if (e.button === 1) {
        App.delete_post()
      }
    })

    DOM.ev(edit, `contextmenu`, (e) => {
      App.edit_post()
      e.preventDefault()
    })
  }

  App.start_embed()

  DOM.ev(document, `dragover`, (e) => {
    e.preventDefault()
  })

  DOM.ev(document, `drop`, (e) => {
    e.preventDefault()
    let files = e.dataTransfer.files

    if (files && (files.length > 0)) {
      App.location(`/`)
    }
  })

  App.setup_scrollers()
  App.setup_refresh()

  DOM.ev(window, `resize`, () => {
    if (App.max_on) {
      App.resize_max()
      App.check_max_editor()
    }
  })

  let user_opts = DOM.el(`#template_user_opts`)

  if (user_opts) {
    App.setup_user_opts()
  }

  let uploader = DOM.el(`#uploader`)

  if (uploader) {
    DOM.evs(uploader, [`click`, `auxclick`], () => {
      App.user_opts_user_id = App.post.user_id
      App.msg_show(`user`)
    })
  }

  let menu = DOM.el(`#menu`)

  if (menu) {
    App.setup_menu_opts()

    DOM.ev(menu, `click`, () => {
      App.msg_show(`menu`)
    })

    DOM.ev(menu, `auxclick`, (e) => {
      if (e.button === 1) {
        App.msg_show(`menu`)
      }
    })

    DOM.ev(menu, `contextmenu`, (e) => {
      App.msg_show(`menu`)
      e.preventDefault()
    })
  }

  let random_btn = DOM.el(`#random`)

  if (random_btn) {
    DOM.ev(random_btn, `click`, () => {
      App.show_random(`menu`, false)
    })

    DOM.ev(random_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        App.random_action(`any`)
      }
    })

    DOM.ev(random_btn, `contextmenu`, (e) => {
      App.show_random(`menu`, false)
      e.preventDefault()
    })
  }

  let next_btn = DOM.el(`#next`)

  if (next_btn) {
    DOM.ev(next_btn, `click`, () => {
      App.show_next()
    })

    DOM.ev(next_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        App.next_action(`any`)
      }
    })

    DOM.ev(next_btn, `contextmenu`, (e) => {
      App.show_next()
      e.preventDefault()
    })
  }

  let vol_btn = DOM.el(`#volume`)

  if (vol_btn) {
    DOM.ev(vol_btn, `click`, () => {
      App.show_volume()
    })

    DOM.ev(vol_btn, `wheel`, (e) => {
      if (e.deltaY < 0) {
        App.volume_up()
      }
      else {
        App.volume_down()
      }

      e.preventDefault()
    })

    DOM.ev(vol_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        App.toggle_volume()
        e.preventDefault()
      }
    })

    DOM.ev(vol_btn, `contextmenu`, (e) => {
      App.show_volume()
      e.preventDefault()
    })
  }

  let play_btn = DOM.el(`#play`)

  if (play_btn) {
    DOM.ev(play_btn, `click`, () => {
      App.toggle_play()
    })

    DOM.ev(play_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        App.pause_video()
      }
    })

    DOM.ev(play_btn, `contextmenu`, (e) => {
      App.toggle_play()
      e.preventDefault()
    })
  }

  let file_btn = DOM.el(`#file_button`)

  if (file_btn) {
    DOM.ev(file_btn, `click`, () => {
      if (App.post.zip_embed) {
        App.show_zip_file_menu()
      }
      else {
        App.download_file()
      }
    })

    DOM.ev(file_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        App.download_file(true)
      }
    })

    DOM.ev(file_btn, `contextmenu`, (e) => {
      App.msgbox(file_btn.dataset.href)
      e.preventDefault()
    })
  }

  let title = DOM.el(`#title`)

  if (title) {
    DOM.ev(title, `click`, () => {
      App.expand_title()
    })
  }

  let cmd = DOM.el(`#cmd`)

  if (cmd) {
    DOM.ev(cmd, `click`, () => {
      App.show_commands()
    })
  }

  App.setup_reactions()
  App.format_description()
  App.setup_video()
  App.create_title_debouncer()
}

App.edit_title = () => {
  let prompt_args = {
    placeholder: `Edit Title`,
    value: App.post.title || App.post.original,
    max: App.max_title_length,
    callback: async (title) => {
      title = title.trim()

      if (!title || (title === App.post.title)) {
        return
      }

      if (App.contains_url(title)) {
        App.popmsg(`Title can't be a URL`)
        return
      }

      App.flash(`Editing`)
      let ids = [App.post.id]

      let response = await fetch(`/edit_title`, {
        method: `POST`,
        headers: {
          "Content-Type": `application/json`,
        },
        body: JSON.stringify({ids, title}),
      })

      App.close_flash()

      if (response.ok) {
        let json = await App.json(response)
        App.post.title = json.title
        DOM.el(`#title`).textContent = App.post.title || App.post.original
        document.title = App.post.title || App.post.name
      }
      else {
        App.feedback(response)
      }
    },
  }

  App.prompt_text(prompt_args)
}

App.edit_description = () => {
  let prompt_args = {
    placeholder: `Edit Description`,
    value: App.post.description,
    max: App.max_description_length,
    multi: true,
    callback: async (description) => {
      description = description.trimEnd()

      if (description === App.post.description) {
        return
      }

      if (App.post.mtype === `mode/talk`) {
        if (!description) {
          App.popmsg(`Description can't be empty`)
          return
        }
      }

      App.flash(`Editing`)
      let ids = [App.post.id]

      let response = await fetch(`/edit_description`, {
        method: `POST`,
        headers: {
          "Content-Type": `application/json`,
        },
        body: JSON.stringify({ids, description}),
      })

      App.close_flash()

      if (response.ok) {
        let json = await App.json(response)
        App.post.description = json.description
        App.format_description()
      }
      else {
        App.feedback(response)
      }
    },
  }

  App.prompt_text(prompt_args)
}

App.edit_filename = () => {
  let prompt_args = {
    placeholder: `Edit Filename`,
    value: App.post.original_full,
    max: App.max_filename_length,
    callback: async (filename) => {
      filename = filename.trimEnd()

      if (filename === App.post.filename) {
        return
      }

      if (!filename) {
        App.popmsg(`Filename can't be empty`)
        return
      }

      App.flash(`Editing`)
      let ids = [App.post.id]

      let response = await fetch(`/edit_filename`, {
        method: `POST`,
        headers: {
          "Content-Type": `application/json`,
        },
        body: JSON.stringify({ids, filename}),
      })

      App.close_flash()

      if (response.ok) {
        App.reload()
      }
      else {
        App.feedback(response)
      }
    },
  }

  App.prompt_text(prompt_args)
}

App.delete_post = () => {
  let confirm_args = {
    message: `Delete this post`,
    callback_yes: () => {
      App.do_delete_post()
    },
  }

  App.confirmbox(confirm_args)
}

App.do_delete_post = async () => {
  let post_id = App.post.id

  let response = await fetch(`/delete_post`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({post_id}),
  })

  if (response.ok) {
    let icon = App.icon(`deleted`)
    DOM.el(`#title`).textContent = `DELETED ${icon}`
    clearInterval(App.refresh_interval)
  }
  else {
    App.feedback(response)
  }
}

App.update_date = () => {
  let [str, level] = App.timeago(App.date_ms)

  if (level > 1) {
    DOM.el(`#ago`).textContent = str
  }
}

App.start_flash = async () => {
  await App.load_script(`/static/ruffle/ruffle.js`)
  let ruffle = window.RufflePlayer.newest()
  let player = ruffle.createPlayer()
  player.id = `flash`
  player.style.width = `800px`
  player.style.height = `600px`
  let container = DOM.el(`#flash_container`)
  container.appendChild(player)
  player.ruffle().load(`/${App.file_path}/${App.post.name}`)
}

App.refresh = async (to_bottom = false) => {
  App.print_info(`Refreshing post...`)
  let post_id = App.post.id

  let response = await fetch(`/refresh`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({post_id}),
  })

  if (response.ok) {
    let json = await App.json(response)
    App.apply_update(json.update)

    if (to_bottom && !App.reversed()) {
      App.to_bottom()
    }
  }
  else {
    App.feedback(response)
  }
}

App.apply_update = (update) => {
  if (update.reactions && update.reactions.length) {
    App.post.reactions = update.reactions
    App.fill_reactions()
  }

  App.post.title = update.title
  document.title = update.post_title
  DOM.el(`#title`).textContent = update.title || App.post.original
  DOM.el(`#views`).textContent = `${update.views} ${update.views === 1 ? `view` : `views`}`
}

App.show_modal_image = () => {
  App.close_corner_msg()
  App.msg_image.show()
}

App.hide_modal_image = () => {
  App.msg_image.close()
}

App.toggle_modal_image = () => {
  App.msg_image.toggle()
}

App.copy_all_text = () => {
  App.copy_to_clipboard(App.post.text || ``)
}

App.select_all_text = () => {
  if (App.editor) {
    App.editor.selectAll()
    return
  }

  let markdown = DOM.el(`#markdown`)

  if (markdown) {
    App.select_all(markdown)
  }
}

App.toggle_max = (what, max_on) => {
  let el = DOM.el(`#${what}`)
  let details = DOM.el(`#details`)
  let buttons = DOM.el(`#text_buttons`)

  if (max_on !== undefined) {
    App.max_on = max_on
  }
  else {
    App.max_on = !App.max_on
  }

  App.max_id = what

  el.style.width = ``
  el.style.height = ``
  el.style.maxWidth = ``
  el.style.maxHeight = ``

  if (App.max_on) {
    DOM.hide(details)

    if (buttons) {
      DOM.hide(buttons)
    }

    el.classList.add(`max`)
    App.resize_max()
  }
  else {
    DOM.show(details)

    if (buttons) {
      DOM.show(buttons)
    }

    el.classList.remove(`max`)
  }

  App.check_max_editor()
}

App.resize_max = () => {
  let w_width = window.innerWidth
  let main = DOM.el(`#main`)
  let left_space = main.getBoundingClientRect().left
  let vwidth = w_width - left_space - 20
  let vheight = App.viewport_height()
  let embed_top = DOM.el(`.embed`).getBoundingClientRect().top
  let mheight = vheight - embed_top

  App.set_css_var(`max_width`, `${vwidth}px`)
  App.set_css_var(`max_height`, `${mheight}px`)
}

App.expand_modal_image = () => {
  if (App.image_expanded) {
    return
  }

  let c = DOM.el(`#modal_image_container`)
  c.classList.add(`expanded`)
  App.image_expanded = true
}

App.reset_modal_image = () => {
  App.reset_image_rotation()
  App.unexpand_modal_image()
}

App.unexpand_modal_image = () => {
  if (!App.image_expanded) {
    return
  }

  let c = DOM.el(`#modal_image_container`)
  c.classList.remove(`expanded`)
  App.image_expanded = false
}

App.on_image_load = () => {
  let img = DOM.el(`#image`)

  if (img) {
    let w = img.naturalWidth
    let h = img.naturalHeight
    DOM.el(`#resolution`).textContent = `${w} x ${h}`
    DOM.show(`#resolution_container`)
  }
}

App.toggle_wrap = () => {
  App.storage.wrapped_editor = !App.wrapped()

  App.editor.setOptions({
    wrap: App.wrapped(),
  })

  App.save_storage()
}

App.guess_mode = () => {
  let modelist = ace.require(`ace/ext/modelist`)
  let modes = modelist.modes

  for (let mode of modes) {
    if (App.post.mtype.includes(mode.name)) {
      return mode.mode
    }
  }

  return `ace/mode/text`
}

App.load_script = (src) => {
  App.print_info(`Loading script: ${src}`)

  return new Promise((resolve, reject) => {
    let script = document.createElement(`script`)
    script.src = src
    script.onload = resolve
    script.onerror = reject
    document.head.appendChild(script)
  })
}

App.start_editor = async () => {
  if (!App.post.text) {
    return
  }

  let scripts = [
    `/static/ace/ace.js`,
    `/static/ace/ext-modelist.js`,
    `/static/ace/theme-tomorrow_night_eighties.js`,
  ]

  for (let src of scripts) {
    await App.load_script(src)
  }

  ace.config.set(`basePath`, `/static/ace`)
  App.editor = ace.edit(`editor`)
  App.editor.setTheme(`ace/theme/tomorrow_night_eighties`)
  let mode = App.guess_mode(App.post.text)
  App.editor.session.setMode(mode)
  App.editor.session.setValue(App.post.text, -1)
  App.editor.setReadOnly(true)
  App.editor.setShowPrintMargin(false)
  let num_lines = App.editor.session.getLength()
  App.editor.renderer.setShowGutter(num_lines > 1)

  App.editor.setOptions({
    wrap: App.wrapped(),
    highlightGutterLine: false,
    showInvisibles: false,
    maxLines: App.editor_lines,
  })
}

App.edit_post = () => {
  App.msg_show(`edit_post`)
}

App.start_embed = () => {
  if (App.post.mtype === `text/markdown`) {
    App.start_markdown()
  }
  else if (App.is_application()) {
    App.start_flash()
  }
  else if (App.post.text) {
    if (App.post.zip_embed) {
      //
    }
    else if (App.post.has_url) {
      if (App.post.youtube_id) {
        App.start_youtube()
      }
      else {
        App.show_url()
      }
    }
    else {
      App.start_editor()
    }
  }

  let image = DOM.el(`#image`)

  if (image) {
    DOM.ev(image, `click`, () => {
      App.show_modal_image()
    })

    DOM.ev(image, `wheel`, (e) => {
      if (e.shiftKey) {
        if (e.deltaY < 0) {
          App.increase_media_size()
        }
        else {
          App.decrease_video_size()
        }

        e.preventDefault()
      }
    })
  }

  let max = DOM.el(`#max`)

  if (max) {
    let type = max.dataset.max_type

    DOM.evs(max, [`click`, `auxclick`], () => {
      App.toggle_max(type)
    })

    DOM.ev(max, `wheel`, (e) => {
      e.preventDefault()

      if (e.deltaY < 0) {
        if (App.max_on) {
          return
        }

        App.increase_media_size()
      }
      else {
        if (App.max_on) {
          App.reset_max()
          return
        }

        App.decrease_video_size()
      }
    })

    DOM.ev(max, `contextmenu`, (e) => {
      App.reset_max()
      e.preventDefault()
    })
  }

  let copy_all = DOM.el(`#copy_all_text`)

  if (copy_all) {
    DOM.ev(copy_all, `click`, () => {
      App.copy_all_text()
    })
  }

  let select_all = DOM.el(`#select_all_text`)

  if (select_all) {
    DOM.ev(select_all, `click`, () => {
      App.select_all_text()
    })
  }

  let toggle_wrap_btn = DOM.el(`#toggle_wrap`)

  if (toggle_wrap_btn) {
    DOM.ev(toggle_wrap_btn, `click`, () => {
      App.toggle_wrap()
    })
  }

  if (App.post.image_embed) {
    App.msg_image = Msg.factory({
      id: `modal_image`,
      class: `modal_image`,
      disable_content_padding: true,
      after_close: () => {
        App.reset_modal_image()

        if (App.corner_mode === `modal_image`) {
          App.close_corner_msg()
        }
      },
    })

    let t = DOM.el(`#template_image`)
    App.msg_image.set(t.innerHTML)
    let img = DOM.el(`#modal_image`)

    DOM.ev(img, `click`, () => {
      App.hide_modal_image()
    })

    DOM.ev(img, `wheel`, () => {
      App.expand_modal_image()
    })
  }

  let video = App.get_video()

  if (video) {
    DOM.ev(video, `wheel`, (e) => {
      if (e.shiftKey) {
        if (e.deltaY < 0) {
          App.increase_media_size()
        }
        else {
          App.decrease_video_size()
        }

        e.preventDefault()
      }
    })
  }
}

App.setup_refresh = () => {
  let delay = 30

  setInterval(function() {
    App.update_date()
  }, 1000 * delay)

  App.update_date()

  if (App.post_refresh_times > 0) {
    App.refresh_interval = setInterval(() => {
      App.refresh()
      App.refresh_count += 1

      if (App.refresh_count >= App.post_refresh_times) {
        clearInterval(App.refresh_interval)
      }
    }, App.post_refresh_interval * 1000)
  }
}

App.start_markdown = async () => {
  await App.load_script(`/static/js/libs/marked.js`)
  let view = DOM.el(`#markdown`)
  let text = view.textContent.trim()
  App.original_markdown = text

  try {
    let html = marked.parse(
      text.replace(/[\u200B-\u200F\uFEFF]/g, ``).trim(),
    )

    DOM.el(`#markdown`).innerHTML = html
  }
  catch (e) {
    App.print_error(e)
  }
}

App.setup_scrollers = () => {
  let r_bottom = DOM.el(`#lobottomy`)

  if (r_bottom) {
    DOM.ev(r_bottom, `click`, () => {
      App.to_bottom()
    })
  }

  let r_top = DOM.el(`#totopia`)

  if (r_top) {
    DOM.ev(r_top, `click`, () => {
      App.to_top()
    })
  }
}

App.edit_privacy = async (privacy) => {
  let ids = [App.post.id]

  let response = await fetch(`/edit_privacy`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({ids, privacy}),
  })

  let json = await App.json(response)

  if (response.ok) {
    App.post.privacy = privacy
    App.update_privacy()
  }
  else {
    App.popmsg(json.message)
  }
}

App.update_privacy = () => {
  let privacy = DOM.el(`#privacy`)
  privacy.textContent = App.capitalize(App.post.privacy)
  let url = new URL(window.location.href)

  if (App.post.privacy !== `private`) {
    url.searchParams.delete(`priv`)
  }
  else {
    url.searchParams.set(`priv`, `true`)
  }

  App.change_menu_icon(`edit_post_opts_privacy`, App.icon(App.post.privacy))
  window.history.replaceState({}, document.title, url.toString())
}

App.start_youtube = () => {
  let video_id = App.post.youtube_id
  let iframe = DOM.create(`iframe`, ``, `youtube`)
  iframe.src = `https://www.youtube.com/embed/${video_id}`
  iframe.title = `YouTube video player`
  iframe.allowFullscreen = true
  let container = DOM.el(`#youtube_container`)
  container.appendChild(iframe)
  DOM.show(container)
}

App.show_url = () => {
  let c = DOM.el(`#url_container`)
  let text = App.safe_html(App.post.text)
  c.innerHTML = `<a href="${text}">${text}</a>`
}

App.format_description = () => {
  if (!App.post.description) {
    DOM.hide(`#description_container`)
    return
  }

  let description = DOM.el(`#description`)

  if (description) {
    let text = App.safe_html(App.post.description)
    text = App.urlize(text)
    description.innerHTML = text

    if (App.is_ascii_art(App.post.description)) {
      description.classList.add(`mono`)
    }
    else {
      description.classList.remove(`mono`)
    }
  }

  DOM.show(`#description_container`)
}

App.wrapped = () => {
  return App.storage_value(`wrapped_editor`, true)
}

App.is_application = () => {
  if (App.post.mtype.startsWith(`application`)) {
    if (App.post.mtype.includes(`flash`)) {
      return true
    }
  }

  return false
}

App.scroll_modal_up = () => {
  let container = DOM.el(App.modal_image_container_id)

  if (container) {
    container.scrollTop -= App.modal_image_scroll_step
  }
}

App.scroll_modal_down = () => {
  let container = DOM.el(App.modal_image_container_id)

  if (container) {
    container.scrollTop += App.modal_image_scroll_step
  }
}

App.change_media_size = (what, size) => {
  function set_height(h) {
    el.style.height = h
    el.style.maxHeight = h
  }

  function set_width(w) {
    el.style.width = w
    el.style.maxWidth = w
  }

  if (App.max_on) {
    return
  }

  let el = DOM.el(`#image`) || App.get_video()

  if (!el) {
    return
  }

  let width = el.clientWidth
  let height = el.clientHeight
  let ratio = height / width
  let original_width = el.style.width
  let original_height = el.style.height
  let new_width = what === `increase` ? width + size : width - size
  let new_height = new_width * ratio

  if (what === `decrease`) {
    if ((new_width < 200) || (new_height < 200)) {
      return
    }
  }

  set_width(`${new_width}px`)
  set_height(`${new_height}px`)

  if (what === `increase`) {
    let actual_width = el.clientWidth
    let actual_height = el.clientHeight
    let actual_ratio = actual_height / actual_width

    if (Math.abs(actual_ratio - ratio) > 0.05) {
      set_width(original_width)
      set_height(original_height)
    }
  }
}

App.increase_media_size = () => {
  App.change_media_size(`increase`, 50)
}

App.decrease_video_size = () => {
  App.change_media_size(`decrease`, 50)
}

App.check_max_editor = () => {
  let mheight = parseInt(App.get_css_var(`max_height`))

  if (App.max_on) {
    if (App.max_id === `editor`) {
      let line_height = App.editor.renderer.line_height || 16
      let max_lines = Math.floor(mheight / line_height) - 2

      App.editor.setOptions({
        maxLines: max_lines > 1 ? max_lines : Infinity,
      })

      App.editor.resize()
    }
  }
  else if (App.max_id === `editor`) {
    App.editor.setOptions({
      maxLines: App.editor_lines,
    })

    App.editor.resize()
  }
}

App.set_volume = (vol) => {
  let video = DOM.el(`video`)

  if (!video) {
    return
  }

  video.muted = false
  vol = App.clamp(vol, 1, 0)
  video.volume = vol
  App.show_volume_feedback()
}

App.show_volume_feedback = () => {
  let video = DOM.el(`video`)

  if (!video) {
    return
  }

  let vol = video.volume
  let feedback = DOM.el(`#volume_feedback`)

  if (feedback) {
    let text = `${Math.round(vol * 100)}%`
    App.set_volume_feedback(text)
  }
}

App.set_volume_feedback = (text) => {
  clearTimeout(App.volume_timeout)
  let feedback = DOM.el(`#volume_feedback`)
  feedback.textContent = text
  DOM.show(feedback)

  App.volume_timeout = setTimeout(() => {
    DOM.hide(feedback)
  }, App.SECOND * 1.6)
}

App.volume_up = (step = 0.05) => {
  let video = DOM.el(`video`)

  if (!video) {
    return
  }

  App.set_volume(video.volume + step)
}

App.volume_down = (step = 0.05) => {
  let video = DOM.el(`video`)

  if (!video) {
    return
  }

  App.set_volume(video.volume - step)
}

App.toggle_volume = () => {
  let video = DOM.el(`video`)

  if (!video) {
    return
  }

  video.muted = !video.muted

  if (video.muted) {
    App.set_volume_feedback(`(M)`)
  }
  else {
    App.show_volume_feedback()
  }
}

App.show_volume = () => {
  App.setup_volume_opts(true)
}

App.set_play_text = (text) => {
  let el = DOM.el(`#play`)

  if (el) {
    el.textContent = text
  }
}

App.toggle_play = () => {
  let video = DOM.el(`video`)

  if (!video) {
    return
  }

  if (video.paused) {
    video.play()
  }
  else {
    video.pause()
  }
}

App.setup_video = () => {
  let video = App.get_video()

  if (!video) {
    return
  }

  DOM.ev(video, `playing`, () => {
    App.set_play_text(`Pause`)

    if (App.video_jump_enabled) {
      App.video_jump_action()
    }
  })

  DOM.ev(video, `pause`, () => {
    App.set_play_text(`Play`)
  })

  DOM.ev(video, `loadeddata`, () => {
    if (typeof App.current_pitch_step !== `undefined`) {
      App.current_pitch_step = 0
    }
  })
}

App.reset_max = () => {
  if (App.max_on && App.max_id) {
    App.toggle_max(App.max_id, false)
  }
}

App.get_file_path = () => {
  let file_btn = DOM.el(`#file_button`)
  return file_btn.dataset.href
}

App.download_file = (new_tab = false, force = false) => {
  function action() {
    let url = App.get_file_path()
    App.goto_url(url, new_tab)
  }

  if (force) {
    action()
    return
  }

  let confirm_args = {
    message: `Download file`,
    callback_yes: () => {
      action()
    },
  }

  App.confirmbox(confirm_args)
}

App.expand_title = () => {
  let title = DOM.el(`#title`)
  title.classList.add(`expanded`)
  title.title = ``
}

App.collapse_title = () => {
  let title = DOM.el(`#title`)
  title.classList.remove(`expanded`)
  title.title = App.get_title()
}

App.create_title_debouncer = () => {
  let title = DOM.el(`#title`)

  App.title_debouncer = App.create_debouncer(() => {
    App.collapse_title()
  }, App.SECOND * 2)

  DOM.ev(title, `mouseleave`, () => {
    App.title_debouncer.call()
  })

  DOM.ev(title, `mouseenter`, () => {
    App.title_debouncer.cancel()
  })
}

App.get_title = () => {
  return App.post.title || App.post.original
}

App.list_zip = async () => {
  let url = App.get_file_path()

  zip.configure({
    useWebWorkers: false,
  })

  let zip_file

  try {
    let reader

    if (zip.HttpReader) {
      reader = new zip.HttpReader(url, {
        useRangeHeader: true,
      })
    }
    else {
      let response = await fetch(url)
      let blob = await response.blob()
      reader = new zip.BlobReader(blob)
    }

    zip_file = new zip.ZipReader(reader)
    let entries = await zip_file.getEntries()

    let file_list = entries.map(entry => {
      let size_str = ``

      if (entry.directory) {
        size_str = `(Dir)`
      }
      else {
        let size = entry.uncompressedSize

        if (size >= 1073741824) { // 1GB
          size_str = `(${(size / 1073741824).toFixed(1)}gb)`
        }
        else if (size >= 1048576) { // 1MB
          size_str = `(${(size / 1048576).toFixed(1)}mb)`
        }
        else if (size >= 1024) { // 1KB
          size_str = `(${(size / 1024).toFixed(1)}kb)`
        }
        else {
          size_str = `(${size}b)`
        }
      }

      let div = DOM.create(`div`)
      div.classList.add(`zip_item`)
      div.textContent = `${entry.filename} ${size_str}`
      return div
    })

    file_list.sort((a, b) => a.textContent.localeCompare(b.textContent))
    let container = DOM.create(`div`)

    for (let item of file_list) {
      container.append(item)
    }

    App.msgbox(container, `html`)
  }
  catch (err) {
    App.print_error(err)
    App.popmsg(`Couldn't list ZIP contents`)
  }
  finally {
    if (zip_file) {
      await zip_file.close()
    }
  }
}

App.show_zip_file_menu = () => {
  App.setup_zip_file_opts(true)
}

App.get_video = () => {
  return DOM.el(`#video`)
}

App.video_percentage = (n) => {
  if ((n < 1) || (n > 9)) {
    return
  }

  let video = App.get_video()

  if (!video) {
    return
  }

  if (!video.duration || isNaN(video.duration)) {
    return
  }

  let p = n * 0.1
  let time = video.duration * p
  video.currentTime = time
}