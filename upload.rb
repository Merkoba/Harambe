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
file_paths = []
image_magic = "off"
audio_magic = "off"
video_magic = "off"
album_magic = "off"
gif_magic = "off"
pastebins = []
pastebin_filenames = []

# Parse command-line options
OptionParser.new do |opts|
  opts.banner = "Usage: upload.rb [options] <file_path1> [file_path2 ...]"

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

# Accept multiple file paths as arguments
ARGV.each do |arg|
  # Remove "file://" prefix if present
  arg = arg.sub(/^file:\/\//, "")
  # Convert to absolute path
  file_paths << File.absolute_path(arg)
end

# Check required parameters
abort("Error: URL is not set") if url.nil? || url.empty?
abort("Error: USERNAME is not set") if username.nil? || username.empty?
abort("Error: PASSWORD is not set") if password.nil? || password.empty?

if file_paths.empty? && pastebins.empty?
  abort("Error: Content is not set")
end

# Prompt to get the title
# If multiple files, prompt for each file's title if --prompt is set
file_titles = []
file_descriptions = []
if prompt && !file_paths.empty?
  file_paths.each do |file_path|
    filename = File.basename(file_path, ".*")
    title = `zenity --entry --title=\"Harambe Upload\" --text=\"Enter a title for #{filename}:\" --entry-text=\"#{filename}\"`.chomp
    if $?.exitstatus != 0
      puts "User cancelled the input."
      exit 1
    end
    file_titles << title

    description = `zenity --entry --title=\"Harambe Upload\" --text=\"Enter a description for #{filename}:\"`.chomp
    if $?.exitstatus != 0
      puts "User cancelled the input."
      exit 1
    end
    file_descriptions << description
  end
elsif prompt && file_paths.empty?
  # No files, just pastebins
  title = `zenity --entry --title=\"Harambe Upload\" --text=\"Enter a title:\"`.chomp
  if $?.exitstatus != 0
    puts "User cancelled the input."
    exit 1
  end
  file_titles << title

  description = `zenity --entry --title=\"Harambe Upload\" --text=\"Enter a description:\"`.chomp
  if $?.exitstatus != 0
    puts "User cancelled the input."
    exit 1
  end
  file_descriptions << description
end

file_paths.each_with_index do |file_path, idx|
  puts "Uploading: #{file_path}"
end

# Make the POST request and capture the response
uri = URI("#{url}/#{endpoint}")
request = Net::HTTP::Post.new(uri)
form_data = []

file_paths.each_with_index do |file_path, idx|
  mime_type = MIME::Types.type_for(file_path).first.to_s
  form_data << [
    "file",
    File.open(file_path),
    {
      filename: File.basename(file_path),
      content_type: mime_type,
    }
  ]
  # If prompting, add a title for each file
  if prompt && file_titles[idx]
    form_data << ["title", file_titles[idx]]
  end
  # If prompting, add a description for each file
  if prompt && file_descriptions[idx]
    form_data << ["description", file_descriptions[idx]]
  end
end

pastebins.each_with_index do |pastebin, index|
  form_data << ["pastebin", pastebin]
  if pastebin_filenames[index] && !pastebin_filenames[index].empty?
    form_data << ["pastebin_filename", pastebin_filenames[index]]
  end
end

# If not prompting, add a single title (empty string or default)
if !prompt
  form_data << ["title", ""]
  form_data << ["description", ""]
end

form_data += [
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