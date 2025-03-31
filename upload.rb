#!/usr/bin/env ruby

require "mime/types"
require "optparse"
require "net/http"
require "uri"
require "json"
require "open3"

# Default values
url = "http://locahost:4040"
username = "yo"
password = "deepwoodz"
endpoint = "205bpm"

# Arguments
prompt = false
zip = "off"
privacy = "public"
file_path = nil
image_magic = "off"
audio_magic = "off"
video_magic = "off"
album_magic = "off"
gif_magic = "off"
pastebins = []
pastebin_filenames = []

# Parse command-line options
OptionParser.new do |opts|
  opts.banner = "Usage: upload.rb [options] <file_path>"

  opts.on("--prompt", "Prompt for the title") do
    prompt = true
  end

  opts.on("--zip", "Compress the file into a zip") do
    zip = "on"
  end

  opts.on("--private", "Make the post private") do
    privacy = "private"
  end

  opts.on("--image-magic", "Do image magic") do
    image_magic = "on"
  end

  opts.on("--audio-magic", "Do audio magic") do
    audio_magic = "on"
  end

  opts.on("--video-magic", "Do video magic") do
    video_magic = "on"
  end

  opts.on("--album-magic", "Do album magic") do
    album_magic = "on"
  end

  opts.on("--gif-magic", "Do gif magic") do
    gif_magic = "on"
  end

  opts.on("--pastebin TEXT", "Create a text file") do |t|
    pastebins << t
  end

  opts.on("--pastebin-filename TEXT", "Filename of the text file") do |t|
    pastebin_filenames << t
  end

  opts.on("-h", "--help", "Prints this help") do
    puts opts
    exit
  end
end.parse!(into: {})

file_path = ARGV[0]

if file_path
  # Remove "file://" prefix if present
  file_path = file_path.sub(/^file:\/\//, "") if file_path

  # Convert to absolute path
  file_path = File.absolute_path(file_path) if file_path
end

# Check required parameters
abort("Error: URL is not set") if url.nil? || url.empty?
abort("Error: USERNAME is not set") if username.nil? || username.empty?
abort("Error: PASSWORD is not set") if password.nil? || password.empty?

if file_path.nil? && pastebins.empty?
  abort("Error: Content is not set")
end

# Prompt to get the title
title = ""

if prompt
  filename = File.basename(file_path, ".*")
  title = `zenity --entry --title="Harambe Upload" --text="Enter a title:" --entry-text="#{filename}"`.chomp

  if $?.exitstatus != 0
    puts "User cancelled the input."
    exit 1
  end
end

puts "Uploading: #{file_path}"

# Make the POST request and capture the response
uri = URI("#{url}/#{endpoint}")
request = Net::HTTP::Post.new(uri)
mime_type = MIME::Types.type_for(file_path).first.to_s
form_data = []

if file_path && !file_path.empty?
  form_data << [
    "file",
    File.open(file_path),
    {
      filename: File.basename(file_path),
      content_type: mime_type,
    }
  ]
end

pastebins.each_with_index do |pastebin, index|
  form_data << ["pastebin", pastebin]

  if pastebin_filenames[index] && !pastebin_filenames[index].empty?
    form_data << ["pastebin_filename", pastebin_filenames[index]]
  end
end

form_data += [
  ["title", title],
  ["username", username],
  ["password", password],
  ["zip", zip],
  ["privacy", privacy],
  ["image_magic", image_magic],
  ["audio_magic", audio_magic],
  ["video_magic", video_magic],
  ["album_magic", album_magic],
  ["gif_magic", gif_magic],
]

request.set_form form_data, "multipart/form-data"

response = Net::HTTP.start(uri.hostname, uri.port, use_ssl: uri.scheme == "https") do |http|
  http.request(request)
end

body = response.body

if response.is_a?(Net::HTTPSuccess)
  full_url = "#{url}/post/#{body}"
  IO.popen(["xclip", "-selection", "clipboard"], "w") { |clipboard| clipboard.print full_url }
  puts "URL Copied: #{full_url}"
  system("awesome-client", 'Utils.msg("Harambe: Upload Complete")')
else
  puts body
end