App.setup_reactions = () => {
  App.icons_loaded = false
  App.selected_icon = ``
  App.setup_reaction_opts()
  let reacts = DOM.el(`#reactions`)

  if (reacts) {
    DOM.ev(reacts, `click`, (e) => {
      let el = e.target.closest(`.reaction_item`)
      App.active_item = el

      if (e.target.classList.contains(`reaction_uname`)) {
        App.user_opts_user_id = el.dataset.user_id
        App.msg_show(`user`)
      }
      else if (e.target.classList.contains(`reaction_ago`)) {
        if (e.target.classList.contains(`button`)) {
          App.msg_show(`reaction`)
        }
      }
    })

    DOM.ev(reacts, `auxclick`, (e) => {
      if (e.button !== 1) {
        return
      }

      let el = e.target.closest(`.reaction_item`)
      App.active_item = el

      if (e.target.classList.contains(`reaction_uname`)) {
        let user_id = el.dataset.user_id
        App.location(`/list/posts?user_id=${user_id}`)
      }
      else if (e.target.classList.contains(`reaction_edit`)) {
        App.active_item.dataset.id
        App.delete_reaction(el.dataset.id)
      }
    })
  }

  let react_btn = DOM.el(`#react_btn`)

  if (react_btn) {
    DOM.ev(react_btn, `click`, () => {
      App.react_prompt()
    })
  }

  let reverse_btn = DOM.el(`#reverse_btn`)

  if (reverse_btn) {
    DOM.ev(reverse_btn, `click`, () => {
      App.toggle_reverse()
    })
  }

  App.fill_reactions()
}

App.reversed = () => {
  return App.storage_value(`reversed_reactions`, false)
}

App.toggle_reverse = () => {
  App.storage.reversed_reactions = !App.reversed()
  App.save_storage()
  App.fill_reactions()
}

App.react_icon = async (id) => {
  if (!App.can_react) {
    App.close_modals()
    App.login_feedback()
    return
  }

  if (!App.icons_loaded) {
    App.msg_icons = Msg.factory({
      disable_content_padding: true,
    })

    let t = DOM.el(`#template_icons`)
    App.msg_icons.set(t.innerHTML)
    await App.fill_icons()
    App.add_icon_events()
  }
  else {
    App.show_all_icons()
  }

  App.icons_id = id
  App.msg_icons.show()
  let input = DOM.el(`#icons_input`)
  input.value = ``
  input.focus()
  App.select_first_icon()
  DOM.el(`#icons`).scrollTop = 0
}

App.filter_icons = () => {
  let r_input = DOM.el(`#icons_input`)
  let value = r_input.value.toLowerCase()
  let icons = DOM.el(`#icons`)
  let children = icons.children

  for (let child of children) {
    if (child.textContent.includes(value)) {
      DOM.show(child)
    }
    else {
      DOM.hide(child)
    }
  }

  App.select_first_icon()
}

App.select_first_icon = () => {
  let icons = DOM.el(`#icons`)
  let children = icons.children
  let selected = false

  for (let child of children) {
    if (selected) {
      child.classList.remove(`selected`)
    }
    else if (!DOM.is_hidden(child)) {
      child.classList.add(`selected`)
      App.selected_icon = child.textContent
      selected = true
    }
  }
}

App.esc_icons = () => {
  let r_input = DOM.el(`#icons_input`)

  if (r_input.value) {
    r_input.value = ``
    App.filter_icons()
  }
  else {
    App.msg_icons.close()
  }
}

App.enter_icons = (item, hide = true) => {
  if (!App.selected_icon) {
    return
  }

  if (hide) {
    App.hide_icons()
  }
  else {
    App.blink(item)
  }

  if (Promptext.instance) {
    Promptext.instance.insert(`:${App.selected_icon}:`)
  }
}

App.hide_icons = () => {
  App.msg_icons.close()
}

App.up_icons = () => {
  let icons = DOM.el(`#icons`)
  let children = Array.from(icons.children)
  let visible = children.filter(c => !DOM.is_hidden(c))

  for (let [i, child] of visible.entries()) {
    if (child.classList.contains(`selected`)) {
      if (i > 0) {
        let prev = visible[i - 1]
        child.classList.remove(`selected`)
        prev.classList.add(`selected`)
        App.selected_icon = prev.textContent
        prev.scrollIntoView({block: `center`})
      }

      break
    }
  }
}

App.down_icons = () => {
  let icons = DOM.el(`#icons`)
  let children = Array.from(icons.children)
  let visible = children.filter(c => !DOM.is_hidden(c))

  for (let [i, child] of visible.entries()) {
    if (child.classList.contains(`selected`)) {
      if (i < (visible.length - 1)) {
        let next = visible[i + 1]
        child.classList.remove(`selected`)
        next.classList.add(`selected`)
        App.selected_icon = next.textContent
        next.scrollIntoView({block: `center`})
      }

      break
    }
  }
}

App.add_reaction = (reaction, check = true) => {
  let reactions = DOM.el(`#reactions`)
  DOM.show(reactions)
  reactions.appendChild(App.make_reaction(reaction))

  if (check) {
    App.check_reactions()
  }
}

App.check_reactions = () => {
  let reactions = DOM.els(`.reaction_item`).length

  if (reactions > 1) {
    DOM.show(`#reverse_container`)
  }

  if (reactions >= 3) {
    DOM.show(`#to_bottom_container`)
    DOM.show(`#totopia`)
  }
}

App.make_reaction = (reaction) => {
  let r = reaction
  let vitem
  vitem = DOM.create(`div`, `reaction_content`)
  vitem.innerHTML = App.text_html(r.value)

  if (!vitem) {
    return
  }

  let t = DOM.el(`#template_reaction_item`)
  let item = DOM.create(`div`, `reaction_item`)
  item.innerHTML = t.innerHTML
  let n = App.max_reaction_name_length
  let name = reaction.uname.substring(0, n).trim()
  DOM.el(`.reaction_uname`, item).textContent = name
  DOM.el(`.reaction_value`, item).appendChild(vitem)
  let ago = DOM.el(`.reaction_ago`, item)

  new Tooltip({
    element: ago,
    generate: () => {
      return dateFormat(r.date * 1000, `d mmmm yyyy hh:MM TT`)
    },
  })

  ago.textContent = reaction.ago
  item.dataset.id = r.id
  item.dataset.user_id = r.user_id
  item.dataset.username = r.username
  item.dataset.value = r.value
  item.dataset.date = r.date

  if ((r.user_id === App.user_id) || App.is_admin) {
    ago.classList.add(`button`)
  }

  return item
}

App.icons_open = () => {
  return App.msg_icons && App.msg_icons.is_open()
}

App.show_all_icons = () => {
  let icons = DOM.el(`#icons`)

  for (let child of icons.children) {
    DOM.show(child)
  }
}

App.get_reaction = (id) => {
  let reactions = DOM.el(`#reactions`)
  let item = reactions.querySelector(`[data-id="${id}"]`)
  return item
}

App.react_prompt = (id) => {
  let value

  if (id) {
    let r = App.get_reaction(id)
    value = r.dataset.value
  }
  else {
    value = ``
  }

  let prompt_args = {
    placeholder: `Write a text reaction`,
    max: App.max_reaction_length,
    value,
    clear: true,
    callback: (text) => {
      if (!text) {
        return
      }

      if (!App.can_react) {
        App.login_feedback()
        return
      }

      let n = App.max_reaction_length
      text = App.remove_multiple_empty_lines(text)
      text = App.replace_urls(text)
      text = Array.from(text).slice(0, n).join(``).trim()

      if (App.contains_url(text)) {
        App.popmsg(`URLs are not allowed`, () => {
          if (Promptext.instance && Promptext.instance.msg.is_open()) {
            Promptext.instance.focus()
          }
        })
        return true
      }

      if (id) {
        App.edit_reaction(id, text)
      }
      else {
        App.send_reaction(text)
      }
    },
    buttons: [
      {
        text: `Icon`,
        callback: () => {
          App.react_icon()
        },
      },
    ],
  }

  App.prompt_text(prompt_args)
}

App.send_reaction = async (text) => {
  if (!App.can_react) {
    return
  }

  text = text.trim()

  if (!text) {
    return
  }

  App.flash(`Sending`)
  let post_id = App.post.id

  let response = await fetch(`/react`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({post_id, text}),
  })

  if (response.ok) {
    await App.refresh(true)
    App.close_flash()
  }
  else {
    App.close_flash()
    App.feedback(response)
  }
}

App.edit_reaction = async (id, text) => {
  if (!App.can_react) {
    return
  }

  let response = await fetch(`/edit_reaction`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({id, text}),
  })

  if (response.ok) {
    let json = await App.json(response)
    App.modify_reaction(json.reaction)
  }
  else {
    App.feedback(response)
  }
}

App.modify_reaction = (reaction) => {
  let item = App.get_reaction(reaction.id)

  if (!item) {
    return
  }

  let new_item = App.make_reaction(reaction)
  item.replaceWith(new_item)
}

App.fill_reactions = () => {
  let reactions = App.post.reactions.slice(0)

  if (App.reversed()) {
    reactions.reverse()
  }

  let c = DOM.el(`#reactions`)
  c.innerHTML = ``

  for (let reaction of reactions) {
    App.add_reaction(reaction, false)
  }

  App.check_reactions()
}

App.delete_reaction = (id) => {
  let confirm_args = {
    message: `Delete this reaction`,
    callback_yes: () => {
      App.do_delete_reaction(id)
    },
  }

  App.confirmbox(confirm_args)
}

App.do_delete_reaction = async (id) => {
  let response = await fetch(`/delete_reaction`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({id}),
  })

  if (response.ok) {
    App.remove_reaction(id)
  }
  else {
    App.feedback(response)
  }
}

App.remove_reaction = (id) => {
  let reactions = DOM.el(`#reactions`)
  let item = reactions.querySelector(`[data-id="${id}"]`)

  if (item) {
    item.remove()
  }

  if (!reactions.children.length) {
    DOM.hide(reactions)
    DOM.hide(`#to_bottom_container`)
    DOM.hide(`#totopia`)
  }
}

App.add_icon_events = () => {
  let input = DOM.el(`#icons_input`)
  let container = DOM.el(`#icons`)

  DOM.ev(input, `input`, () => {
    App.filter_icons()
  })

  DOM.ev(input, `keydown`, (e) => {
    if (e.key === `Escape`) {
      App.esc_icons()
      e.preventDefault()
    }
    else if (e.key === `Enter`) {
      App.enter_icons()
      e.preventDefault()
    }
    else if (e.key === `ArrowUp`) {
      App.up_icons()
      e.preventDefault()
    }
    else if (e.key === `ArrowDown`) {
      App.down_icons()
      e.preventDefault()
    }
  })

  DOM.ev(container, `click`, (e) => {
    if (e.target.closest(`.icon_item`)) {
      let item = e.target.closest(`.icon_item`)
      App.selected_icon = item.dataset.icon
      App.enter_icons(item)
    }
  })

  DOM.ev(container, `auxclick`, (e) => {
    if (e.button === 1) {
      if (e.target.closest(`.icon_item`)) {
        let item = e.target.closest(`.icon_item`)
        App.selected_icon = item.dataset.icon
        App.enter_icons(item, false)
      }
    }
  })
}

App.fill_icons = async () => {
  App.flash(`Fetching`)
  let container = DOM.el(`#icons`)
  let response = await fetch(`/get_icons`)
  App.close_flash()

  if (!response.ok) {
    App.feedback(response)
    return
  }

  App.icons_loaded = true
  let json = await App.json(response)
  let icons = App.shuffle_array(json.icons)

  for (let icon of icons) {
    let item = DOM.create(`div`, `icon_item`)
    let text = DOM.create(`div`, `icon_item_text`)
    text.textContent = icon
    item.appendChild(text)
    let img = DOM.create(`img`, `icon_item_img`)
    img.loading = `lazy`
    img.src = `/static/icons/${icon}.gif`
    item.appendChild(img)
    item.dataset.icon = icon
    container.appendChild(item)
  }
}