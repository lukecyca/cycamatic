-- at which intervals should the screen switch to the
-- next image?
local INTERVAL = 12

-- enough time to load next image
local SWITCH_DELAY = 8

-- transition time in seconds.
-- set it to 0 switching instantaneously
local SWITCH_TIME = 0.8

assert(SWITCH_TIME + SWITCH_DELAY < INTERVAL,
    "INTERVAL must be longer than SWITCH_DELAY + SWITCHTIME")

gl.setup(NATIVE_WIDTH, NATIVE_HEIGHT)
math.randomseed( os.time() )

local font = resource.load_font("SADSLices-Regular.otf")

local function shuffle( a )
    local c = #a
    for i = 1, (c * 20) do
        local ndx0 = math.random( 1, c )
        local ndx1 = math.random( 1, c )
        local temp = a[ ndx0 ]
        a[ ndx0 ] = a[ ndx1 ]
        a[ ndx1 ] = temp
    end
    return a
end

-- Load all picture files into table, shuffled
local pictures = {}
for name, _ in pairs(CONTENTS) do
    if name:match(".*jpg") or name:match(".*JPG") then
        table.insert(pictures, math.random(1, #pictures), name)
    end
end
print("Loaded images: ")
for k, v in pairs(pictures) do
    print("    " .. v)
end

node.event("content_remove", function(filename)
    for k, v in pairs(pictures) do
        if filename == v then
            table.remove(pictures, k)
            print("Removed " .. filename)
        end
    end
end)

local new_pictures = {}
node.event("content_update", function(filename)
    print("Detected " .. filename)
    for k, v in pairs(pictures) do
        if filename == v then
            print("Skipped " .. filename)
            return
        end
    end
    if filename:match(".*jpg") or filename:match(".*JPG") then
        print("Added " .. filename)
        table.insert(new_pictures, filename)
    end
end)

local current_image, fade_start
local current_image_num = 1

local function next_image()
    local next_image_name

    if #new_pictures > 0 then
        table.insert(pictures, current_image_num, table.remove(new_pictures, 1))
    end

    next_image_name = pictures[current_image_num]
    print("now loading " .. current_image_num .. ":" .. next_image_name)

    last_image = current_image
    current_image = resource.load_image(next_image_name)
    fade_start = sys.now()

    current_image_num = current_image_num + 1
    if current_image_num > #pictures then
        shuffle(pictures)
        current_image_num = 1
    end
end

util.set_interval(INTERVAL, next_image)

function node.render()
    gl.clear(0,0,0,1)

    if current_image == nil then
        return
    end

    local delta = sys.now() - fade_start - SWITCH_DELAY
    if last_image and delta < 0 then
        draw_full(last_image, 0, 0, WIDTH, HEIGHT)
    elseif last_image and delta < SWITCH_TIME then
        local progress = delta / SWITCH_TIME
        draw_full(last_image, 0, 0, WIDTH, HEIGHT, 1 - progress)
        draw_full(current_image, 0, 0, WIDTH, HEIGHT, progress)
    else
        if last_image then
            last_image:dispose()
            last_image = nil
        end
        draw_full(current_image, 0, 0, WIDTH, HEIGHT)
    end
    --font:write(98, 38, "See your photos on Instagram @JurkeAndBill", 80, 0, 0, 0, 1)
    --font:write(100, 40, "See your photos on Instagram @JurkeAndBill", 80, 1, 1, 1, 1)
end

function draw_full(obj, x1, y1, x2, y2, alpha)
    --assumes x1 = x2 = 0

    local img_w, img_h = obj:size()
    local img_aspect_ratio = img_w / img_h
    local viewport_aspect_ratio = x2 / y2

    if img_aspect_ratio < viewport_aspect_ratio then
        -- constained by width, compensate height
        local scale_by = x2 / img_w
        local h_adj = (img_h * scale_by - y2) / 2
        pcall(function()
            obj:draw(0, -h_adj, img_w * scale_by, img_h * scale_by - h_adj, alpha)
        end)
    else
        -- constrained by height, compensate width
        local scale_by = y2 / img_h
        local w_adj = (img_w * scale_by - x2) / 2
        pcall(function()
            obj:draw(-w_adj, 0, img_w * scale_by - w_adj, img_h * scale_by, alpha)
        end)
    end
end
