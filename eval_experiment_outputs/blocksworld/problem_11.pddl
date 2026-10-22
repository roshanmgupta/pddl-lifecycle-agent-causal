(define (problem blocksworld_50_blocks)
  (:domain blocksworld)

  (:objects
    b1 - block
    b2 - block
    b3 - block
    b4 - block
    b5 - block
    b6 - block
    b7 - block
    b8 - block
    b9 - block
    b10 - block
    b11 - block
    b12 - block
    b13 - block
    b14 - block
    b15 - block
    b16 - block
    b17 - block
    b18 - block
    b19 - block
    b20 - block
    b21 - block
    b22 - block
    b23 - block
    b24 - block
    b25 - block
    b26 - block
    b27 - block
    b28 - block
    b29 - block
    b30 - block
    b31 - block
    b32 - block
    b33 - block
    b34 - block
    b35 - block
    b36 - block
    b37 - block
    b38 - block
    b39 - block
    b40 - block
    b41 - block
    b42 - block
    b43 - block
    b44 - block
    b45 - block
    b46 - block
    b47 - block
    b48 - block
    b49 - block
    b50 - block
  )

  (:init
    (ontable b1)
    (ontable b11)
    (ontable b26)
    (ontable b36)
    (ontable b46)
    (ontable b47)
    (ontable b48)
    (ontable b49)
    (ontable b50)
    (on b2 b1)
    (on b3 b2)
    (on b4 b3)
    (on b5 b4)
    (on b6 b5)
    (on b7 b6)
    (on b8 b7)
    (on b9 b8)
    (on b10 b9)
    (on b12 b11)
    (on b13 b12)
    (on b14 b13)
    (on b15 b14)
    (on b16 b15)
    (on b17 b16)
    (on b18 b17)
    (on b19 b18)
    (on b20 b19)
    (on b21 b20)
    (on b22 b21)
    (on b23 b22)
    (on b24 b23)
    (on b25 b24)
    (on b27 b26)
    (on b28 b27)
    (on b29 b28)
    (on b30 b29)
    (on b31 b30)
    (on b32 b31)
    (on b33 b32)
    (on b34 b33)
    (on b35 b34)
    (on b37 b36)
    (on b38 b37)
    (on b39 b38)
    (on b40 b39)
    (on b41 b40)
    (on b42 b41)
    (on b43 b42)
    (on b44 b43)
    (on b45 b44)
    (clear b10)
    (clear b25)
    (clear b35)
    (clear b45)
    (clear b46)
    (clear b47)
    (clear b48)
    (clear b49)
    (clear b50)
    (handempty)
  )

  (:goal (and (on b1 b2) (on b2 b3) (on b3 b4) (on b4 b5) (on b5 b6) (on b6 b7) (on b7 b8) (on b8 b9) (on b9 b10) (on b10 b11) (on b11 b12) (on b12 b13) (on b13 b14) (on b14 b15) (on b15 b16) (on b16 b17) (on b17 b18) (on b18 b19) (on b19 b20) (on b20 b21) (on b21 b22) (on b22 b23) (on b23 b24) (on b24 b25) (on b25 b26) (on b26 b27) (on b27 b28) (on b28 b29) (on b29 b30) (ontable b30) (on b50 b49) (on b49 b48) (on b48 b47) (on b47 b46) (on b46 b45) (on b45 b44) (on b44 b43) (on b43 b42) (on b42 b41) (on b41 b40) (on b40 b39) (on b39 b38) (on b38 b37) (on b37 b36) (on b36 b35) (on b35 b34) (on b34 b33) (on b33 b32) (on b32 b31) (ontable b31)))
)